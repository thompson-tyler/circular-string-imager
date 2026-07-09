from time import time


class FatherTimer:

    @staticmethod
    def format_time(time_sec: float):
        hours = int(time_sec // 3600)
        minutes = int((time_sec % 3600) // 60)
        seconds = int(time_sec % 60)
        fractional = int((time_sec - int(time_sec)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{fractional:03d}"
    
    @staticmethod
    def now():
        return time()

    def __init__(self):
        self.times = {}
        self.start_time = time()
        self.lap_start = self.start_time
        self.laps = []
        self.total_time = 0
    
    def __str__(self):
        report_lines = ["Timing Profile:"]

        for context, elapsed in self.times.items():
            total_elapsed = sum(elapsed)
            total = FatherTimer.format_time(total_elapsed)
            average = FatherTimer.format_time(total_elapsed / len(elapsed))
            report_lines.append(f"  {context}: total={total}, average={average}, % of total={total_elapsed / self.total_time * 100 if self.total_time > 0 else 0:.2f}%")
            if len(elapsed) > 1:
                take_every = len(elapsed) // 20
                for i in range(0, len(elapsed), take_every + 1):
                    lap_time = elapsed[i]
                    formatted_lap_time = FatherTimer.format_time(lap_time)
                    report_lines.append(f"    Lap {i + 1}: {formatted_lap_time}")

        if len(self.laps) > 0:
            report_lines.append("Lap times:")
        for i, lap_time in enumerate(self.laps):
            formatted_lap_time = FatherTimer.format_time(lap_time)
            report_lines.append(f"  Lap {i + 1}: {formatted_lap_time}")

        report_lines.append(f"Total logged time: {FatherTimer.format_time(self.total_time)}")
        report_lines.append(f"Total elapsed time: {FatherTimer.format_time(time() - self.start_time)}")
        return "\n".join(report_lines)

    def _add_time(self, context, elapsed):
        if context is not None:
            if context not in self.times:
                self.times[context] = []
            self.times[context].append(elapsed)
        self.total_time += elapsed

    class TimerSon:
        father_timer: "FatherTimer"
        start_time: float

        def __init__(self, father_timer, context=None):
            self.father_timer = father_timer
            self.context = context
            self.start_time = time()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()
        
        def stop(self):
            elapsed = time() - self.start_time
            self.father_timer._add_time(self.context, elapsed)
    
    def timer(self, context=None):
        return self.TimerSon(self, context)
    
    def elapsed_time(self):
        return time() - self.start_time
    
    def lap(self):
        current_time = self.now()
        new_lap_time = current_time - self.lap_start
        self.lap_start = current_time
        self.laps.append(new_lap_time)
        return new_lap_time
    
    def report(self):
        print(self.__str__())
