from collections import deque


class PlanScheduler:

    def schedule(self, plan):

        queue = deque()

        for milestone in plan.milestones:
            for job in milestone.jobs:
                for task in job.tasks:
                    queue.append(task)

        return queue

    def next(self, queue):

        if not queue:
            return None

        return queue.popleft()


scheduler = PlanScheduler()
