# countryplotter.py

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from urllib.request import urlretrieve

import pycountry # you didn't have this installed did you and your code failed

class FlagScatterPlot:
    def __init__(self):
        os.makedirs("flags", exist_ok=True)

    def country_to_iso_code(self, name):
        try:
            return pycountry.countries.lookup(name).alpha_2.lower()
        except LookupError:
            return None

    def get_flag_image(self, country_name):
        code = self.country_to_iso_code(country_name)
        if not code:
            return None
        filename = f"flags/{code}.png"
        if not os.path.exists(filename):
            url = f"https://flagcdn.com/w40/{code}.png"
            try:
                urlretrieve(url, filename)
            except Exception:
                return None
        return mpimg.imread(filename)

# alter axes here
    def plot(self, data, x_label="Big Mac % Change", y_label="Threshold 2526 vs UK (%)", title=None):
        """
        Data is a list of tuples: (country, bm_pct, pct_vs_uk)
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            ax.set_title(title)
    
        # Plot each point using the flag image as marker
        for country, bm_pct, pct_vs_uk in data:
            img = self.get_flag_image(country)
            if img is not None:
                im = OffsetImage(img, zoom=0.4)
                ab = AnnotationBbox(im, (bm_pct, pct_vs_uk), frameon=False)
                ax.add_artist(ab)
            else:
                ax.plot(bm_pct, pct_vs_uk, 'o', label=country)
    
        # Center is at (0, 100)
        center_x, center_y = 0, 100
        x_vals = [x for (_, x, _) in data]
        y_vals = [y for (_, _, y) in data]
    
        # Compute max absolute distance from center for each axis
        max_dx = max(abs(x - center_x) for x in x_vals)
        max_dy = max(abs(y - center_y) for y in y_vals)
    
        # Set symmetric limits around (0, 100)
        xlim = (-max_dx, max_dx)
        ylim = (center_y - max_dy, center_y + max_dy)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    
        # Draw quadrant lines
        ax.axhline(center_y, color='black', linestyle='--', linewidth=2)
        ax.axvline(center_x, color='black', linestyle='--', linewidth=2)
        ax.set_aspect('equal', adjustable='box') 
        ax.grid(True)
        plt.tight_layout()
        plt.show()

