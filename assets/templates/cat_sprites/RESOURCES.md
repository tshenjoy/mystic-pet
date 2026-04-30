# Cat Sprite Resources for Desktop Pet Customization

This directory contains open-source cat sprite resources collected from OpenGameArt.org. Each resource has been evaluated for suitability to be used as a template for personalization (fur color recoloring, eye color adjustment, etc.).

## Overview

These resources will serve as **base templates** for the customization pipeline:
1. Extract dominant fur colors from user's uploaded cat photo (KMeans clustering)
2. Recolor sprites using the extracted colors via PNG sprite sheet manipulation
3. Optionally adjust eye color and other features based on photo analysis

**Key Requirement:** Resources should have:
- ✅ Simple pixel art style (easy to recolor)
- ✅ Minimal color palette (4-8 colors ideal)
- ✅ Good walking stance in side profile view
- ✅ Clear head and torso separation
- ✅ PNG or convertible format (avoid complex GIFs)

---

## Resource Inventory

### 1. Shepardskin Cat Sprites
**Directory:** `01_shepardskin/cat sprite/`

**License:** No attribution required (most permissive)

**Source:** https://opengameart.org/content/cat-sprites

**Characteristics:**
- Pixel art style
- Simple 4-color palette (ideal for recoloring)
- Multiple animation states with varying scales (x2, x4)
- Includes: walking, running, and still frames
- GIF format animations

**Files:**
- `catspritesx2.gif` – Walking animation (2x scale)
- `catspritesx4.gif` – Walking animation (4x scale)
- `catrunx2.gif` – Running animation (2x scale)
- `catrunx4.gif` – Running animation (4x scale)
- `catwalkx2.gif` – Alternative walk cycle (2x)
- `catwalkx4.gif` – Alternative walk cycle (4x)
- `catspritesoriginal.gif` – Original scale reference

**Post-processing Difficulty:** ⭐ **VERY EASY**
- Minimal colors = easier color replacement
- Simple shapes = good for programmatic recoloring
- **RECOMMENDATION:** Use as primary template

---

### 2. Orange Fat Cat
**File:** `02_orange_fat_cat.zip` (to be downloaded)

**License:** CC0 (Public Domain – zero restrictions!)

**Source:** https://opengameart.org/content/orange-fat-cat

**Characteristics:**
- **50+ individual PNG files** (frame-by-frame, not GIF)
- Pixel art style, simple colors
- Multiple animations: Idle (2 frames), Walk (19 frames), Jump (10 frames), Dead (15 frames)
- Complete sprite sheets provided
- Transparent background (PNG)
- **Excellent for color substitution due to flat color blocks**

**Animations:**
- Idle poses (including zombie cat variant)
- Walk cycle (19 frames = smooth, detailed animation)
- Jump mechanic
- Death/falling

**Post-processing Difficulty:** ⭐⭐ **EASY**
- PNG format = precise RGB color replacement
- Individual frames available = can recolor frame-by-frame or as batch
- Flat color palette = predictable for color mapping
- 19-frame walk cycle = very smooth animation
- **RECOMMENDATION:** EXCELLENT secondary template; highly suitable for recoloring

**Why suitable:**
- ✅ Multiple PNGs (no GIF complexity)
- ✅ Comprehensive animation set
- ✅ CC0 license (no attribution needed)
- ✅ Proven popular (1372 downloads)

---

### 3. Cats - Pixel Art (by peony)
**File:** `03_cats_pixel_art.zip` (to be downloaded)

**License:** CC0 (Public Domain – zero restrictions!)

**Source:** https://opengameart.org/content/cats-pixel-art

**Characteristics:**
- **16×16 pixel tiles** – very small, simple
- Multiple color variations: grey, beige (siamese), black, white, orange
- Includes: Head, Paw, Eyes (dilated & normal), Full body, Accessories (Catnip, Yarn, Bell, Mouse, Fish)
- Pure pixel art style
- Excellent color palette reference

**Post-processing Difficulty:** ⭐ **VERY EASY**
- Tiny size = minimal colors per sprite
- Perfect for understanding color composition
- Useful as a **testing ground for color extraction pipeline**
- Multiple existing color variants = can validate KMeans extraction against known outputs
- **RECOMMENDATION:** EXCELLENT for testing & validation; use as reference

**Why suitable:**
- ✅ Extremely simple (easy to debug recoloring)
- ✅ Multiple color variants provided (validate against them!)
- ✅ CC0 license
- ✅ Pure RGB, no indexed color issues

---

### 4. Pixel Cat (by scofanogd)
**File:** `04_pixel_cat.png` (to be downloaded)

**License:** CC0 (Public Domain – zero restrictions!)

**Source:** https://opengameart.org/content/pixel-cat

**Characteristics:**
- Single small sprite (~32×32px estimate)
- Minimalist pixel art cat
- Simple pose
- Perfect color palette for learning/testing
- File size: 2.1 KB (extremely minimal)

**Post-processing Difficulty:** ⭐ **VERY EASY**
- Minimal pixel art = maximum simplicity
- Great for prototyping color transformation
- Good baseline for understanding color substitution
- **RECOMMENDATION:** Use as minimal reference/test case

**Why suitable:**
- ✅ Simplest possible cat sprite
- ✅ CC0 license
- ✅ Good for validating color substitution logic

---

## Usage Strategy for Customization Pipeline

### Step 1: Select Base Template
- **Primary:** Shepardskin (simplest, 4-color palette, good stance)
- **Secondary:** Orange Fat Cat (19-frame walk cycle, multiple animations)
- **Testing:** Cats - Pixel Art (validate color extraction against known variants)
- **Reference:** Pixel Cat (minimal sprite for baseline testing)

### Step 2: Extract Colors from User's Photo
```
User photo → OpenCV face detection → Pillow crop → KMeans color extraction
```

### Step 3: Recolor Base Sprites (PNG Format Only!)
Use PIL/Pillow to:
- Load PNG sprite sheet (single image, not GIF)
- Map template colors to extracted fur colors via pixel-level transformation
- Optionally adjust eye color based on photo analysis
- Preserve sprite structure and animation frame layout

**Key:** Use PNG sprite sheets, NOT GIFs, for efficient color substitution.
See GIF_EDITING_ANALYSIS.md for why PNG is superior for recoloring.

### Step 4: Export Personalized Sprite Sheet
- Generate composite sprite sheet (all frames in PNG format)
- Maintain animation frame timing in metadata.json
- Store in `cache/` for runtime use
- Keep both original template and personalized version

---

## Attribution Requirements

| Resource | License | Attribution Required |
|----------|---------|----------------------|
| Shepardskin | No attribution | ❌ No |
| Orange Fat Cat | CC0 | ❌ No |
| Cats - Pixel Art | CC0 | ❌ No |
| Pixel Cat | CC0 | ❌ No |

---

## Technical Notes for Implementation

### Color Mapping Strategy
The selected resources use simple color palettes (4-8 colors):
- **Body color** (main fur) – PRIMARY TARGET for recoloring
- **Darker shade** (shadows, outline, definition) – SECONDARY, auto-darken primary
- **Eyes** (black/dark center + white highlights) – Detect and substitute separately
- **Nose/mouth** (pink or similar) – Can recolor or keep neutral
- **Background** (transparency) – Preserve

**KMeans Extraction Pipeline:**
1. Extract dominant colors from user's cat photo (e.g., top 3-5 colors by frequency)
2. Map template colors → extracted colors using closest-match in RGB space
3. Apply substitution to sprite sheet

### Sprite Dimensions
- Shepardskin: ~40×40px (original), 80×80px (2x), 160×160px (4x)
- Orange Fat Cat: ~128×128px per sprite (larger, detailed)
- Cats - Pixel Art: 16×16px tiles (tiny, minimal)
- Pixel Cat: ~32×32px (small, minimal)

### Animation Frame Counts
- Walk: 4-19 frames (Shepardskin has 4, Orange Fat Cat has 19)
- Idle: 2-4 frames
- Run/Chase: 4-6 frames

### Format Requirements
✅ **APPROVED:** PNG (single sprite sheet or individual PNGs)
❌ **AVOID:** GIF (complex frame-by-frame recoloring, indexed color issues)
❌ **AVOID:** Layered source files (.xcf, .psd) – too heavy for runtime

---

## Next Steps

1. **Download new resources:** Orange Fat Cat, Cats - Pixel Art, Pixel Cat
2. **Convert Shepardskin GIFs → PNG sprite sheets** (extract frames, composite)
3. **Prototype recoloring:** Test color substitution on Shepardskin sprites
4. **Validate against Cats - Pixel Art:** Use peony's color variants as test cases
5. **Build sprite generator:** Implement `customization/sprite_generator.py`
6. **Test with real photos:** Run full pipeline on sample cat images

---

**Last Updated:** April 30, 2026
**Status:** Resources refined; ready to download and integrate
