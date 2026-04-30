# Cat Sprite Resources for Desktop Pet Customization

This directory contains 5 open-source cat sprite resources collected from OpenGameArt.org. Each resource has been evaluated for suitability to be used as a template for personalization (fur color recoloring, eye color adjustment, etc.).

## Overview

These resources will serve as **base templates** for the customization pipeline:
1. Extract dominant fur colors from user's uploaded cat photo (KMeans clustering)
2. Recolor sprites using the extracted colors
3. Optionally adjust eye color and other features based on photo analysis

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

### 2. Sergeant Cat
**File:** `02_sergeant_cat.png`

**License:** CC-BY 3.0 (requires attribution: link to www.GameBuildingTools.com)

**Source:** https://opengameart.org/content/sergeant-cat

**Characteristics:**
- Sprite sheet format
- 6 individual frames in vertical layout (118×900px)
- Clear side-profile walking stance
- Endless runner game art style
- More detailed than Shepardskin

**Frames:** 6 sequential walking frames

**Post-processing Difficulty:** ⭐⭐ **EASY**
- Larger pixel size = easier to work with
- Good frame separation
- More detail = slightly more complex recoloring but clearer anatomy
- **RECOMMENDATION:** Excellent fallback; use for walking animation reference

---

### 3. Pirate Cat
**File:** `03_pirate_cat.png`

**License:** CC-BY 3.0 (requires attribution: link to www.GameBuildingTools.com)

**Source:** https://opengameart.org/content/pirate-cat

**Characteristics:**
- Sprite sheet format
- 6 frames in vertical layout (59×450px)
- Related to Sergeant Cat (same game project)
- Running/walking animation
- Smaller dimensions than Sergeant Cat

**Post-processing Difficulty:** ⭐⭐ **EASY**
- Consistent with Sergeant Cat style
- Smaller size = less detail but still workable
- Good alternative stance for variety
- **RECOMMENDATION:** Use as secondary walking variant or running animation

---

### 4. Happy/Cool Cat
**File:** `04_happy_cool_cat.png`

**License:** CC-BY 3.0 (requires attribution: link to www.GameBuildingTools.com)

**Source:** https://opengameart.org/content/happy-cat

**Characteristics:**
- Sprite sheet format
- 6 frames in vertical layout (118×900px)
- Yellow/warm-toned cat (different from others)
- Same dimensions and style as Sergeant Cat
- From the same game project

**Post-processing Difficulty:** ⭐⭐ **EASY**
- Identical format to Sergeant Cat
- Good for testing color extraction & recoloring
- Useful reference for eye color variation
- **RECOMMENDATION:** Use for testing color transformation pipeline

---

### 5. Fat Side-scroller Cat
**File:** `05_fat_sidescroller_cat.7z` (requires 7-Zip extraction)

**License:** CC0 (Public Domain – zero restrictions!)

**Source:** https://opengameart.org/content/fat-side-scroller-cat

**Characteristics:**
- 8-frame walk cycle
- Includes GIMP source files (.xcf)
- More detailed pixel art (rounder, "fluffier" style)
- Larger sprite size = more workable for scaling
- Alternative aesthetic (less angular than others)

**Post-processing Difficulty:** ⭐⭐⭐ **MODERATE**
- More detailed/complex pixel patterns
- Larger size = more pixel manipulation needed
- Better scalability than others
- Source files included = can modify base sprites if needed
- **RECOMMENDATION:** Use if detail level needs to increase; best license (CC0)

---

## Usage Strategy for Customization Pipeline

### Step 1: Select Base Template
- **Primary:** Shepardskin (simplest, no attribution required)
- **Fallback:** Sergeant Cat or Happy Cat (good frame quality)

### Step 2: Extract Colors from User's Photo
```
User photo → OpenCV face detection → Pillow crop → KMeans color extraction
```

### Step 3: Recolor Base Sprites
Use PIL's `ImageDraw` or similar to:
- Map template colors to extracted fur colors
- Optionally adjust eye color
- Preserve sprite structure and animation frames

### Step 4: Export Personalized Sprite Sheet
- Generate composite sprite sheet
- Maintain animation frame timing
- Store in `cache/` for runtime use

---

## Attribution Requirements

| Resource | License | Attribution Required |
|----------|---------|----------------------|
| Shepardskin | No attribution | ❌ No |
| Sergeant Cat | CC-BY 3.0 | ✅ Yes (GameBuildingTools.com) |
| Pirate Cat | CC-BY 3.0 | ✅ Yes (GameBuildingTools.com) |
| Happy Cat | CC-BY 3.0 | ✅ Yes (GameBuildingTools.com) |
| Fat Side-scroller | CC0 | ❌ No |

---

## Technical Notes for Implementation

### Color Mapping
The Shepardskin sprites use a simple color palette (~4 colors):
- Body color (main fur)
- Darker shade (eyes, outline, shadow)
- Possibly white (eyes, belly)
- Background transparency

KMeans clustering on user photo can extract:
1. Primary fur color
2. Secondary fur color (shading)
3. Eye color
4. White/highlight color

Then map original sprite colors → new colors in RGB space.

### Sprite Dimensions
- Shepardskin: ~40×40px (original), 80×80px (2x), 160×160px (4x)
- Sergeant/Happy/Pirate: ~118×150px per frame
- Fat Cat: ~80×96px per frame (larger, scalable)

### Animation Timing (from metadata.json)
- Walk: 10 FPS, 4-8 frames
- Run/Chase: 12 FPS, 4-6 frames
- Idle: 5 FPS, 4 frames

Consider frame counts when selecting template.

---

## Next Steps

1. **Extract and process:** Convert GIFs to PNG frame sequences for easier manipulation
2. **Prototype recoloring:** Test color replacement on Shepardskin sprites
3. **Build sprite generator:** Implement automated recoloring pipeline (customization/sprite_generator.py)
4. **Test with real photos:** Validate color extraction and eye detection on sample cat photos
5. **Composite & cache:** Generate personalized sprite sheets on first run

---

**Last Updated:** April 30, 2026
