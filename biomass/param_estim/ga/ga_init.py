import time
import numpy as np

from .converter import decode_gene2variable
from .undx_mgg import mgg_alternation
from .converging import converging
from .local_search import local_search
from biomass.param_estim.fitness import objective
from biomass.param_estim.search_parameter import search_parameter_index
from biomass.param_estim.search_parameter import get_search_region


def optimize(nth_paramset):

    np.random.seed(
        time.time_ns()*nth_paramset % 2**32
    )
    search_idx = search_parameter_index()
    search_region = get_search_region()

    max_generation = 10000
    n_population = int(5*search_region.shape[1])
    n_children = 50
    n_gene = search_region.shape[1]
    allowable_error = 0.35

    (best_indiv, best_fitness) = ga_v2(
        nth_paramset,
        max_generation,
        n_population,
        n_children,
        n_gene,
        allowable_error,
        search_idx,
        search_region
    )


def ga_v1(nth_paramset, max_generation, n_population, n_children, n_gene,
          allowable_error, search_idx, search_region):
    population = get_initial_population(
        nth_paramset, n_population, n_gene, search_idx, search_region
    )
    with open('./out/%d/out.log' % (nth_paramset), mode='w') as f:
        f.write(
            'Generation1: Best Fitness = %e\n' % (
                population[0, -1]
            )
        )
    best_indiv = decode_gene2variable(
        population[0, :n_gene], search_region
    )
    best_fitness = population[0, -1]

    np.save(
        './out/%d/generation.npy' % (
            nth_paramset
        ), 1
    )
    np.save(
        './out/%d/fit_param1' % (
            nth_paramset
        ), best_indiv
    )
    np.save(
        './out/%d/best_fitness.npy' % (
            nth_paramset
        ), best_fitness
    )
    if population[0, -1] <= allowable_error:
        best_indiv = decode_gene2variable(
            population[0, :n_gene], search_region
        )
        best_fitness = population[0, -1]
        return best_indiv, best_fitness

    while generation < max_generation:
        population = mgg_alternation(
            population, n_population, n_children, n_gene, search_idx, search_region
        )
        best_indiv = decode_gene2variable(
            population[0, :n_gene], search_region
        )
        if population[0, -1] < best_fitness:
            np.save(
                './out/%d/generation.npy' % (
                    nth_paramset
                ), generation + 1
            )
            np.save(
                './out/%d/fit_param%d.npy' % (
                    nth_paramset, generation + 1
                ), best_indiv
            )
        best_fitness = population[0, -1]
        np.save(
            './out/%d/best_fitness.npy' % (
                nth_paramset
            ), best_fitness
        )
        np.save(
            './out/%d/count_num.npy' % (
                nth_paramset
            ), generation + 1
        )
        with open('./out/%d/out.log' % (nth_paramset), mode='a') as f:
            f.write(
                'Generation%d: Best Fitness = %e\n' % (
                    generation + 1, best_fitness
                )
            )
        if population[0, -1] <= allowable_error:
            best_indiv = decode_gene2variable(
                population[0, :n_gene], search_region
            )
            best_fitness = population[0, -1]
            return best_indiv, best_fitness

        generation += 1

    best_indiv = decode_gene2variable(
        population[0, :n_gene], search_region
    )
    best_fitness = population[0, -1]

    return best_indiv, best_fitness


def ga_v2(nth_paramset, max_generation, n_population, n_children, n_gene,
          allowable_error, search_idx, search_region):
    if n_population < n_gene + 2:
        raise ValueError(
            'n_population must be larger than %d' % (
                n_gene + 2
            )
        )
    n_iter = 1
    n0 = np.empty(2*n_population)

    population = get_initial_population(
        nth_paramset, n_population, n_gene, search_idx, search_region
    )
    n0[0] = population[0, -1]

    with open('./out/%d/out.log' % (nth_paramset), mode='w') as f:
        f.write(
            'Generation1: Best Fitness = %e\n' % (
                population[0, -1]
            )
        )
    best_indiv = decode_gene2variable(
        population[0, :n_gene], search_region
    )
    best_fitness = population[0, -1]

    np.save(
        './out/%d/generation.npy' % (
            nth_paramset
        ), 1
    )
    np.save(
        './out/%d/fit_param1.npy' % (
            nth_paramset
        ), best_indiv
    )
    np.save(
        './out/%d/best_fitness.npy' % (
            nth_paramset
        ), best_fitness
    )
    if population[0, -1] <= allowable_error:
        best_indiv = decode_gene2variable(
            population[0, :n_gene], search_region
        )
        best_fitness = population[0, -1]
        return best_indiv, best_fitness

    generation = 1
    while generation < max_generation:
        ip = np.random.choice(n_population, n_gene+2, replace=False)
        ip, population = converging(
            ip, population, n_population, n_gene, search_idx, search_region
        )
        ip, population = local_search(
            ip, population, n_population, n_children, n_gene, search_idx, search_region
        )
        for _ in range(n_iter-1):
            ip = np.random.choice(n_population, n_gene+2, replace=False)
            ip, population = converging(
                ip, population, n_population, n_gene, search_idx, search_region
            )
        if generation % len(n0) == 0:
            n0 = np.empty_like(n0)
            n0[0] = population[0, -1]
        elif generation % len(n0) == len(n0)-1:
            n0[-1] = population[0, -1]
            if n0[0] == n0[-1]:
                n_iter *= 2
            else:
                n_iter = 1
        else:
            n0[generation % len(n0)] = population[0, -1]

        best_indiv = decode_gene2variable(
            population[0, :n_gene], search_region
        )
        if population[0, -1] < best_fitness:
            np.save(
                './out/%d/generation.npy' % (
                    nth_paramset
                ), generation + 1
            )
            np.save(
                './out/%d/fit_param%d.npy' % (
                    nth_paramset, generation + 1
                ), best_indiv
            )
        best_fitness = population[0, -1]
        np.save(
            './out/%d/best_fitness.npy' % (
                nth_paramset
            ), best_fitness
        )
        np.save(
            './out/%d/count_num.npy' % (
                nth_paramset
            ), generation + 1
        )
        with open('./out/%d/out.log' % (nth_paramset), mode='a') as f:
            f.write(
                'Generation%d: Best Fitness = %e\n' % (
                    generation + 1, best_fitness
                )
            )
        if population[0, -1] <= allowable_error:
            best_indiv = decode_gene2variable(
                population[0, :n_gene], search_region
            )
            best_fitness = population[0, -1]
            return best_indiv, best_fitness

        generation += 1

    best_indiv = decode_gene2variable(
        population[0, :n_gene], search_region
    )
    best_fitness = population[0, -1]

    return best_indiv, best_fitness


def get_initial_population(nth_paramset, n_population, n_gene, search_idx, search_region):
    population = np.full((n_population, n_gene+1), np.inf)

    with open('./out/%d/initpop.log' % (nth_paramset), mode='w') as f:
        f.write(
            'Generating the initial population. . .\n'
        )
    for i in range(n_population):
        while np.isinf(population[i, -1]) or np.isnan(population[i, -1]):
            population[i, :n_gene] = np.random.rand(n_gene)
            population[i, -1] = objective(
                population[i, :n_gene], search_idx, search_region
            )
        with open('./out/%d/initpop.log' % (nth_paramset), mode='a') as f:
            f.write(
                '%d/%d\n' % (
                    i + 1, n_population
                )
            )
    population = population[np.argsort(population[:, -1]), :]

    return population
