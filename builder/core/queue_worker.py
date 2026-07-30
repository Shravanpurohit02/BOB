from builder.core.tasks import queue


class QueueWorker:

    def process(self):

        completed = 0

        while len(queue):

            task = queue.next()

            if task is None:
                break

            completed += 1

        return completed


worker = QueueWorker()
