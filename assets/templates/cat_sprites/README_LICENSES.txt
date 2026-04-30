# License and Attribution Information

## Resource Licenses

### 1. Shepardskin Cat Sprites
- **License:** No attribution required (public/free use)
- **Source:** https://opengameart.org/content/cat-sprites
- **Author:** Shepardskin
- **Attribution:** Optional - "Credit Shepardskin and/or https://twitter.com/Shepardskin"

### 2. Orange Fat Cat
- **License:** CC0 (Public Domain)
- **Source:** https://opengameart.org/content/orange-fat-cat
- **Author:** megupets
- **Attribution:** Optional - "megupets.com (if you wish)"
- **Why This One:** 50+ PNG files, multiple animations (idle, walk, jump, dead), 19-frame smooth walk cycle

### 3. Cats - Pixel Art
- **License:** CC0 (Public Domain)
- **Source:** https://opengameart.org/content/cats-pixel-art
- **Author:** peony
- **Attribution:** Not required
- **Why This One:** Multiple color variants (grey, beige, black, white, orange) = perfect for validating color extraction pipeline

### 4. Pixel Cat
- **License:** CC0 (Public Domain)
- **Source:** https://opengameart.org/content/pixel-cat
- **Author:** scofanogd
- **Attribution:** Not required
- **Why This One:** Minimal sprite for baseline testing and prototyping

---

## Why We Removed Resources 2-4 from Previous Version

The original selection included:
- Sergeant Cat (CC-BY 3.0)
- Pirate Cat (CC-BY 3.0)
- Happy Cat (CC-BY 3.0)
- Fat Side-scroller Cat (CC0)

**Decision:** These were replaced because:
1. Attribution requirements (CC-BY needs active linking)
2. Less suitable for color substitution pipeline
3. Limited frame variety compared to Orange Fat Cat
4. GIF complications with Fat Cat
5. Better alternatives found with CC0 and more animations

**New selection prioritizes:**
✅ CC0 licenses (zero restrictions, no attribution overhead)
✅ PNG format (easier color recoloring)
✅ Simple pixel art (easier to process)
✅ Multiple color variants (validation testing)
✅ Rich animation sets (more usable)

---

## Attribution Recommendations for Final Product

### In Application
Include in About/Credits dialog:

```
Cat Sprites (Resources for customization):
- Shepardskin Cat Sprites (no attribution required)
- Orange Fat Cat by megupets (CC0)
- Cats - Pixel Art by peony (CC0)
- Pixel Cat by scofanogd (CC0)

All resources sourced from OpenGameArt.org
```

### In Source Code
No CC-BY licenses to comply with = no linking requirements needed!
Just include resources in assets/ folder with credit to OpenGameArt.org.

---

## Compliance Notes

- **Green for distribution:** All resources are CC0 or no-attribution
- **No commercial restriction:** All can be used in commercial projects
- **Derivative works:** Can create personalized versions without additional licensing
- **Attribution:** Optional for all selected resources
- **Simplification:** Much cleaner than previous selection with CC-BY requirements
