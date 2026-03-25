---
name: dealerspike-landing-pages
description: Workflow for creating location + product SEO landing pages in the DealerSpike CMS for Thermo King of North Florida (thermokingjax.com). Use this skill whenever the user wants to create new location pages, find missing location+product combos, add new geo or product keyword pages, or update content assets in the DealerSpike CMS. Also trigger when the user says "let's do [product] for [location]", asks to audit existing pages, or wants to fill content gaps on thermokingjax.com.
---

# DealerSpike Landing Pages — Thermo King of North Florida

## Site & CMS Info

- **CMS**: https://dealerspike-cms.com/Sites/Pages
- **Live site**: https://www.thermokingjax.com
- **Phone**: (904) 388-6692
- **Address**: 2733 Pickettville Rd, Jacksonville, FL 32220
- **Tools needed**: Claude in Chrome (browser automation)

## URL Slug Pattern

```
/[product-slug]-in-[city-slug]-fl
```

Examples:
- `/cargo-rail-in-orange-park-fl`
- `/apu-in-atlantic-beach-fl`
- `/coldtainer-in-yulee-fl`

## Page SEO Fields

| Field | Format |
|-------|--------|
| Page Title | `Thermo King [Product] in [City], FL` |
| HTML Title Tag | `Thermo King [Product] in [City], FL` |
| Page File Name | `/[product-slug]-in-[city-slug]-fl` |
| Meta Description | `Welcome to Thermo King of [City], FL Your Trusted Source for Thermo King [Product] \| (904) 388-6692` |
| Meta Keywords | `Thermo King of [City], FL, Thermo King [Product]` |

Set Meta Description and Meta Keywords to **Custom** (not Pre-Optimized).

## Known Products & Their Page URLs

| Product | Product URL Slug (on thermokingjax.com) |
|---------|----------------------------------------|
| Cargo Rail | `/new-models/thermo-king-rail-cargo-rail-1966653598735190563225964` |
| APU (TriPAC) | `/new-models/thermo-king-tripac-apu-apu-1966607385711498286334316` |
| Coldtainer® | *(check live site — search for Coldtainer product page)* |
| Heat King | *(check live site)* |
| Marine Refrigeration | *(check live site)* |

When the product URL is unknown, navigate to thermokingjax.com and find the correct product page URL before building assets.

## Workflow

### Step 1 — Gap Analysis (optional but recommended)

1. Navigate to https://dealerspike-cms.com/Sites/Pages
2. Scroll through the full page list and note all existing `[Product] in [City], FL` pages
3. Build a matrix of existing combos (product × location)
4. Identify missing combos and propose them to the user before creating

Common locations: Jacksonville, Atlantic Beach, Jacksonville Beach, Fernandina Beach, Lakeside, Orange Park, Yulee, Ponte Vedra Beach, St. Augustine, Fleming Island, Middleburg, Palatka

### Step 2 — Create the Page

1. Click **Add Page**
2. Fill in all SEO fields (see table above)
3. Make sure Meta Description and Meta Keywords radio buttons are set to **Custom**
4. Click **Save** — *the page must be saved before you can add an asset*

### Step 3 — Create the Content Asset

After saving the page, the Primary Content section becomes active:

1. Click **Add New Asset**
2. Set the **Title** field to match the page title exactly: `Thermo King [Product] in [City], FL`
3. Click the **`</>`** (source code) button in the WYSIWYG toolbar — do NOT type into the visual editor
4. Select all existing content in the source editor (Ctrl+A) and delete it
5. Paste the full HTML template (see `assets/template.html`) with substitutions made:
   - Replace every `[CITY]` with the city name (e.g., `Orange Park`)
   - Replace every `[PRODUCT]` with the product name (e.g., `Cargo Rail`)
   - Replace every `[PRODUCT_URL]` with the full product page URL
6. Click **Save**
7. Click **Back** to return to the page edit form
8. Click **Save** on the page

### Step 4 — Verify

Navigate to the live URL (`https://www.thermokingjax.com/[slug]`) and confirm:
- The h2 heading shows the correct city and product
- All sections render (Why Choose, Features, What We Offer, Testimonials, CTA)
- Product links point to the correct product page

## Important Notes

- **Save page before adding asset** — the Add New Asset button does nothing on an unsaved page
- **Always use source view** (`</>` button) to paste HTML — the visual editor will strip the `<style>` block
- **Edit button** in the asset row requires a direct left click; if it doesn't respond, try clicking slightly left of center on the button
- **Back navigation** after saving an asset sometimes returns to the asset edit page rather than the page list — navigate directly to https://dealerspike-cms.com/Sites/Pages if needed
- Product keywords and geo keywords must appear in: the h2, the intro paragraph, all linked anchor text, the "Why Choose" section, "What We Offer" section, "Why Customers Trust" section, "Additional Benefits" section, testimonials, and the CTA

## Product-Specific Feature Bullets

The "Our Thermo King [PRODUCT] Features" section uses product-specific bullets. Replace `[PRODUCT_FEATURES]` in the template with the appropriate set below:

### Cargo Rail
```html
<li dir="ltr">Evergreen CARB compliant engine (TK488CR)</li>
<li>No need for Diesel Particulate Filter (DPF)</li>
<li dir="ltr">Delivers double digit fuel savings</li>
```

### APU (TriPAC)
```html
<li dir="ltr">Significantly reduces engine idle time and fuel consumption</li>
<li dir="ltr">Provides cab heating and cooling while the main engine is off</li>
<li dir="ltr">Delivers substantial fuel savings compared to idling — improving driver comfort and your bottom line</li>
```

### Coldtainer®
```html
<li dir="ltr">Portable, self-powered refrigerated container — works independently of the vehicle engine</li>
<li dir="ltr">Wide temperature range suitable for pharmaceuticals, fresh food, and perishable cargo</li>
<li dir="ltr">Intermodal compatible — moves seamlessly between trucks, vans, and ground transport</li>
```

### Heat King
```html
<li dir="ltr">Hydronic heating system designed for temperature-sensitive cargo</li>
<li dir="ltr">Runs on the truck's existing diesel fuel — no separate fuel source required</li>
<li dir="ltr">Ideal for liquid cargo, chemicals, and food products requiring consistent heat</li>
```

### Marine Refrigeration
```html
<li dir="ltr">Marine-grade corrosion-resistant construction built for harsh saltwater environments</li>
<li dir="ltr">Reliable temperature control designed specifically for marine vessel applications</li>
<li dir="ltr">Full sales, service, and parts support from certified Thermo King marine technicians</li>
```

## Template

The full HTML template is in `assets/template.html`. Before pasting:

1. Replace `[CITY]` → city name (e.g., `Ponte Vedra Beach`)
2. Replace `[PRODUCT]` → product name (e.g., `Cargo Rail`)
3. Replace `[PRODUCT_URL]` → full product URL (e.g., `https://www.thermokingjax.com/new-models/thermo-king-rail-cargo-rail-1966653598735190563225964`)
4. Replace `[PRODUCT_FEATURES]` → the product-specific feature bullets from the section above
