from nids.baseline.baseline_calculator import BaselineCalculator
print('?? Menghitung baseline dengan UTC time...')
BaselineCalculator.compute_and_store(window_minutes=120)
print('? Selesai!')
