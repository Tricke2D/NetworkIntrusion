from nids.baseline.baseline_calculator import BaselineCalculator
print('?? Menghitung baseline dari 62 samples...')
BaselineCalculator.compute_and_store(window_minutes=30)
print('? Selesai!')
