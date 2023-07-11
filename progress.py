import time
from datetime import datetime


class ProgressBar:
    """Progress bar for pretty progress displaying with various features."""

    def __init__(
        self,
        maximum: int,
        message: str,
        end_message: str = None,
        show_numbers: bool = True,
        timed: bool = False,
        end_time: bool = True,
        extended: bool = None,
        segments: int = 20,
        symbol: str = "=",
        extended_symbol: str = "-",
        extend_segments: int = 10,
    ):
        """Progress bar for pretty progress displaying with various features.

        Args:
            maximum (int): maximum value (equals 100%)
            message (str): name of the currently ongoing task. Can be emtpty
            end_message (str, optional): message that will replace the progress bar on end. Defaults to None.
            show_numbers (bool, optional): should the actual numbers be displays? Defaults to True.
            timed (bool, optional): should the execution time be measured? Defaults to False.
            end_time (bool, optional): print the total time at the end. Defaults to True.
            extended (bool, optional): should there be a subdevision? Defaults to None.
            segments (int, optional): number of segments for the bar. Defaults to 20.
            symbol (str, optional): progress symbol. Defaults to "=".
            extended_symbol (str, optional): subdevision progress symbol. Defaults to "-".
            extend_segments (int, optional): number of subdevision segments. Defaults to 10.
        """
        self.max = maximum
        self.msg = message
        self.end_msg = end_message
        self.segments = segments
        if extended is None:
            self.extended = maximum >= self.segments * 10
        else:
            self.extended = extended
        self.extend_segments = extend_segments
        self.show_numbers = show_numbers
        self.symbol = symbol
        self.extended_symbol = extended_symbol

        self.__status_msg = ""
        self.__cur = 0
        self.__next_clean = 0

        self.timed = timed
        self.end_time = end_time
        if self.timed:
            self.__start_time = time.time()
            self.__last_time = None
            self.__times = []
            self.__cur_time = None
            self.__total_time = None
        elif self.end_time:
            self.__start_time = time.time()

    def tick(self, step: int = 1):
        """Add progress to the progressbar and print out the current status

        Args:
            step (int, optional): Progress increment. Defaults to 1.
        """
        self.__cur += step

        if self.timed:
            if self.__last_time:
                self.__cur_time = time.time() - self.__last_time
                self.__times.append(self.__cur_time)
                if len(self.__times) > 5:
                    self.__times.pop(0)
            self.__last_time = time.time()
            self.__total_time = time.time() - self.__start_time

        self.__print()

    def update(self):
        """Updates the progress bar without progressing it.
        Especially useful for updating the current time.
        """
        if self.timed:
            self.__total_time = time.time() - self.__start_time

        self.__print()

    def print(self, message: str):
        """Prints a message and ensures proper formatting with the progress bar.

        Args:
            message (str): Message to print
        """
        self.clean()
        print(message)
        self.__print()

    def __print(self):
        cur_length = int((self.__cur / self.max) * self.segments)
        text = f"{self.msg} [{self.symbol * cur_length}{' ' * (self.segments - cur_length)}]"
        if self.show_numbers:
            text += f" {self.__cur}/{self.max}"
        if self.timed and self.__cur_time:
            iter = 1 / (sum(self.__times) / len(self.__times))
            text += f" ({self.__format_time(self.__total_time)}|{iter:.1f}it/s)"
        if self.extended:
            rest = self.__cur - (cur_length * (self.max / self.segments))
            extend_length = (
                int((rest / (self.max / self.segments)) * self.extend_segments) + 1
            )
            text += f" {self.extended_symbol * (extend_length - 1)}>{' ' * (self.extend_segments - extend_length + 1)}"
        if self.__status_msg:
            text += f" - {self.__status_msg}"
        if self.__next_clean:
            text += " " * self.__next_clean
            self.__next_clean = 0
        print(
            text,
            end="\r",
        )
        if self.__cur >= self.max:
            self.end()

    def __format_time(self, time: float):
        date = datetime.fromtimestamp(time)
        if date.minute < 1:
            return date.strftime("%S.%f")[:-4] + "s"
        return date.strftime("%M:%S.%f")[:-4]

    def end(self):
        """Force the progress bar to be completed."""
        if not self.end_msg:
            print("")
            return
        self.clean()
        text = self.end_msg
        if self.end_time:
            text += f"  [in {self.__format_time(time.time() - self.__start_time)}]"
        print(text)

    def clean(self):
        """Cleans the console from the current progress bar prints."""
        max_length = len(self.msg) + self.segments + 5
        if self.show_numbers:
            max_length += 2 + len(str(self.max)) * 2
        if self.timed:
            max_length += 25
        if self.extended:
            max_length += 4 + self.extend_segments
        if self.__status_msg:
            max_length += len(self.__status_msg) + 3
        print(" " * max_length, end="\r")

    def status(self, message: str = ""):
        """Display a status message that is visible besides the current status. Only one status can be active at any time

        Args:
            message (str, optional): Status message to display. Empty string removes the current status. Defaults to "".
        """
        self.__next_clean = len(self.__status_msg) + 3
        self.__status_msg = message


if __name__ == "__main__":
    print("Testing Progressbar!")

    count = 1000
    sleep = 10 / count
    bar = ProgressBar(count, "Testing...", end_message="Testing complete!", timed=True)
    k = 1
    for i in range(count):
        if i == 250:
            bar.status("Getting started!")
        if i == 600:
            bar.status("Heavy lifting...")
        if i == 700:
            bar.status()
        if i == 900:
            bar.status("Nearly done!")
        if i >= 600 and i < 700:
            if i % 10 == 0:
                bar.print(f"Test {k}... Complete!")
                k += 1
            time.sleep(sleep * 3)
        bar.tick()
        time.sleep(sleep)
