"""Pluggable circuit-generation backends for AutoEIS.

Circuit generation is the *only* stage of the pipeline that depends on Julia
(via ``EquivalentCircuits.jl``). This module is the seam that isolates that
dependency: everything Julia-specific about generating candidate circuits lives
behind the :class:`CircuitBackend` interface, so an alternative search (a
pure-Python implementation, a different solver, a mock for tests) can be dropped
in without the rest of the package knowing or caring.

Contract
--------
A backend receives impedance data plus search parameters and returns candidate
circuits as **strings in EquivalentCircuits.jl's output form**::

    'EquivalentCircuit("R1-[P2,R3]", (R1 = 139.1, P2w = 1.2e-5, P2n = 0.9, R3 = 4.6e6,))'

That format is what :func:`autoeis.io.parse_ec_output` consumes downstream. The
topology grammar is ``-`` for series and ``[ , ]`` for parallel, with component
letters ``R`` (resistor), ``C`` (capacitor), ``L`` (inductor), and ``P``
(constant-phase element). Everything after generation (filtering, Bayesian
inference, metrics) is pure Python and never touches a backend.

Usage
-----
Swap the process-wide default::

    import autoeis as ae
    ae.set_default_backend(MyBackend())

or override for a single call::

    ae.generate_equivalent_circuits(freq, Z, backend=MyBackend())
"""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

import numpy as np
import psutil
from tqdm.auto import tqdm

from autoeis.julia_helpers import ec, jl
from autoeis.utils import flush_streams

log = logging.getLogger(__name__)


@runtime_checkable
class CircuitBackend(Protocol):
    """Structural interface every circuit-generation backend must satisfy.

    Implement :meth:`generate` with this exact signature and return a list of
    circuit strings in EquivalentCircuits.jl output form (see the module
    docstring). Because this is a :class:`~typing.Protocol`, a backend need not
    subclass anything; matching the method signature is sufficient, and
    ``isinstance(obj, CircuitBackend)`` works at runtime.
    """

    def generate(
        self,
        freq: np.ndarray,
        Z: np.ndarray,
        *,
        iters: int,
        complexity: int,
        tol: float,
        generations: int,
        population_size: int,
        terminals: str,
        parallel: bool,
        seed: int,
    ) -> list[str]:
        """Return candidate circuits as strings.

        The parameters mirror the public search knobs of
        :func:`autoeis.core.generate_equivalent_circuits`. ``seed`` is always a
        concrete integer (the caller resolves ``None`` to a value); the backend
        is responsible for seeding its own RNG so a given seed is reproducible.
        """
        ...


class JuliaBackend:
    """Default backend: the genetic-programming search in EquivalentCircuits.jl.

    This class is the single owner of Julia-specific generation logic. It holds
    the two things the rest of AutoEIS no longer needs to know about:

    1. the translation from AutoEIS's domain parameters (``complexity``, ``tol``,
       ...) to the keyword names EquivalentCircuits.jl expects, and
    2. the serial and Julia-parallel execution strategies, including RNG
       seeding and progress reporting.
    """

    def generate(
        self,
        freq: np.ndarray,
        Z: np.ndarray,
        *,
        iters: int,
        complexity: int,
        tol: float,
        generations: int,
        population_size: int,
        terminals: str,
        parallel: bool,
        seed: int,
    ) -> list[str]:
        search_kwargs = self._build_search_kwargs(
            complexity=complexity,
            tol=tol,
            generations=generations,
            population_size=population_size,
            terminals=terminals,
        )
        run = self._generate_parallel if parallel else self._generate_serial
        return run(freq, Z, iters, search_kwargs, seed)

    @staticmethod
    def _build_search_kwargs(
        *,
        complexity: int,
        tol: float,
        generations: int,
        population_size: int,
        terminals: str,
    ) -> dict:
        """Map AutoEIS domain parameters to EquivalentCircuits.jl keyword names."""
        return {
            "head": complexity,
            "terminals": terminals,
            "convergence_threshold": tol,
            "generations": generations,
            "population_size": population_size,
        }

    @staticmethod
    def _seed_rng(seed: int) -> None:
        """Seed Julia's global RNG so a given ``seed`` yields a reproducible run."""
        jl.seval(f"import Random; Random.seed!({seed})")

    def _generate_serial(
        self,
        freq: np.ndarray,
        Z: np.ndarray,
        iters: int,
        search_kwargs: dict,
        seed: int,
    ) -> list[str]:
        """Evolve one circuit per iteration in a single process."""
        self._seed_rng(seed)

        circuits = []
        for _ in tqdm(range(iters), desc="Generating Candidate ECMs", leave=False):
            flush_streams()
            try:
                circuit = ec.circuit_evolution(Z, freq, **search_kwargs, quiet=True)
            except Exception as exc:  # noqa: BLE001 - Julia errors surface as generic Exceptions
                log.error(f"Error generating circuit: {exc}")
                continue
            circuits.append(circuit)
        flush_streams()

        return [str(c) for c in circuits if c is not None]

    def _generate_parallel(
        self,
        freq: np.ndarray,
        Z: np.ndarray,
        iters: int,
        search_kwargs: dict,
        seed: int,
    ) -> list[str]:
        """Evolve circuits using EquivalentCircuits.jl's batched (Julia-side) parallelism.

        The batch call exposes no per-iteration hook, so the requested iterations
        are chunked across the physical cores and the batch is invoked once per
        chunk, purely so a progress bar can advance.
        """
        # NOTE: Seeding here does not propagate into Julia's worker processes, so
        # a parallel run is not bit-for-bit reproducible from ``seed`` alone.
        # Fixing this requires seeding each worker (Julia's ``@everywhere``); use
        # the serial path when exact reproducibility matters.
        self._seed_rng(seed)

        n_workers = psutil.cpu_count(logical=False)
        # Oversubscribe to buffer slow-converging runs, but only when there are
        # enough iterations that the progress bar still conveys something.
        if (iters // n_workers) > 10:
            n_workers *= 2

        # e.g. iters=11, n_workers=4 -> chunks = [4, 4, 3]
        chunks = [n_workers] * (iters // n_workers)
        if iters % n_workers:
            chunks.append(iters % n_workers)

        circuits = []
        with tqdm(
            total=iters, desc="Generating Candidate ECMs", miniters=1, leave=False
        ) as pbar:
            flush_streams()
            for chunk in chunks:
                try:
                    batch = ec.circuit_evolution_batch(
                        Z, freq, **search_kwargs, iters=chunk, quiet=True
                    )
                except Exception as exc:  # noqa: BLE001
                    log.error(f"Error generating circuits: {exc}")
                    batch = []
                circuits += batch
                pbar.update(chunk)
                flush_streams()

        return [str(c) for c in circuits if c is not None]


_default_backend: CircuitBackend | None = None


def get_default_backend() -> CircuitBackend:
    """Return the process-wide default backend, creating a :class:`JuliaBackend` on first use."""
    global _default_backend
    if _default_backend is None:
        _default_backend = JuliaBackend()
    return _default_backend


def set_default_backend(backend: CircuitBackend) -> None:
    """Install ``backend`` as the process-wide default used by circuit generation."""
    global _default_backend
    _default_backend = backend
