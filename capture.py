import numpy as np
from mss import mss

class Capture:
    """
    Capture sınıfı, belirtilen bir ekran bölgesini yakalamaktan sorumludur.
    """

    def __init__(self, x, y, x_fov, y_fov):
        """
        Capture sınıfını ekran yakalama parametreleri ile başlatır.

        Args:
            x (int): Yakalama başlangıç noktası için X koordinatı.
            y (int): Yakalama başlangıç noktası için Y koordinatı.
            x_fov (int): Yakalama alanının genişliği.
            y_fov (int): Yakalama alanının yüksekliği.
        """
        self.monitor = {
            "top": y,
            "left": x,
            "width": x_fov,
            "height": y_fov
        }
        
    def get_screen(self):
        """
        Belirtilen bölgeye göre ekranı yakalar ve numpy dizisi olarak döndürür.

        Returns:
            np.ndarray: Yakalanan ekran bölgesi numpy dizisi olarak.
        """
        with mss() as sct:
            screenshot = sct.grab(self.monitor)
            return np.array(screenshot)