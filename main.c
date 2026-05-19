#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 1000
#define NUM_THREADS 4

int array[ARRAY_SIZE];
long partial_sums[NUM_THREADS]; 

void* sum_array(void* arg) {
    int thread_id = *(int*)arg;
    int start = thread_id * (ARRAY_SIZE / NUM_THREADS);
    int end = (thread_id + 1) * (ARRAY_SIZE / NUM_THREADS);
    
    partial_sums[thread_id] = 0;
    for (int i = start; i < end; i++) {
        partial_sums[thread_id] += array[i];
    }
    
    printf("Потік %d: порахував суму від індексу %d до %d = %ld\n", thread_id, start, end - 1, partial_sums[thread_id]);
    pthread_exit(NULL);
}

int main() {
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];

    for (int i = 0; i < ARRAY_SIZE; i++) array[i] = 1;

    for (int i = 0; i < NUM_THREADS; i++) {
        thread_ids[i] = i;
        pthread_create(&threads[i], NULL, sum_array, (void*)&thread_ids[i]);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    long total_sum = 0;
    for (int i = 0; i < NUM_THREADS; i++) {
        total_sum += partial_sums[i];
    }

    printf("------------------------------------------\n");
    printf("Результат: загальна сума масиву = %ld\n", total_sum);
    
    return 0;
}