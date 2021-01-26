def submit_and_execute_single_job(executor, func, job_args):
    future = executor.submit(func, *job_args)
    return future
