from dataclasses import dataclass

@dataclass
class ReplayState:
    timestamps: list[str]
    index: int = 0
    playing: bool = False
    speed: int = 1
    def current(self): return self.timestamps[self.index] if self.timestamps else None
    def play(self): self.playing=True
    def pause(self): self.playing=False
    def reset(self): self.index=0; self.playing=False
    def step(self):
        if self.timestamps: self.index=min(self.index+1,len(self.timestamps)-1)
        return self.current()
