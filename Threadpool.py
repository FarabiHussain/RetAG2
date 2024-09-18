import threading


class Threadpool():
    def __init__(self) -> None:
        self.pool = []
        self.index = 0

    def create(self, target=None):
        print(target)
        newThread = threading.Thread(target=target)
        self.pool.append(newThread)
        self.pool[self.index].start()
        curr_index = self.index
        self.index += 1

        return (curr_index)

    def join_index(self, index):
        self.pool[index].join()
        self.index -= 1

    def join_all(self):
        for t in self.pool:
            print(t)
            t.join()
            self.index -= 1