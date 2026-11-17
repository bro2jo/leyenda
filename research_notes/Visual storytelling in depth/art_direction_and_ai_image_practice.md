# Art direction and AI image practice for an illustrated fantasy serial (in-depth pass)

Research date: 2026-11-17. This pass checks the earlier notes (`research_notes/Visual storytelling for the Chronicle/art_direction_and_ai_image_practice.md`) against full primary pages, corrects them, and adds new material.

**Read status.** Each claim is marked **(full page read)** when I read the page itself, or **(summary only)** when the claim rests on a search-engine summary or excerpt. Evidence labels: **[Official]** vendor docs or announcements; **[Primary]** a creator talking about their own work; **[Paper]** academic paper or preprint; **[Secondary]** press or analysis; **[Weak]** vendor blog, tutorial, forum or unsourced summary.

**Network notes.** Full reads worked for developers.openai.com, arxiv.org, gdcvault.com (session abstracts only; talk videos have no transcript), www.gamedeveloper.com, www.pcgamer.com, www.frontiersin.org and www.nngroup.com. Two hosts on the allowed list could not be read:
- **help.openai.com** and **docs.midjourney.com** answered the plain client with a bot-check page (HTTP 403, "Just a moment…"), and the fetch tool could not resolve them. I did not try to get around the bot check, so their claims below are summary only.
- **link.springer.com** was refused by the proxy (403 on CONNECT) despite being on the list.

openai.com, updates.midjourney.com, media.gdcvault.com (the slide PDFs) and www.gdcvault.com were blocked, so those claims are summary only too.

---

## 1. OpenAI image models in ChatGPT and the API (verified against official pages)

### Takeaway
As of 17 November 2026 the current OpenAI image models are **GPT-Image-2.6 Sunburst and GPT-Image-2.6 Flare**. The developer docs say "For new integrations, use GPT-Image-2.6 Sunburst or Flare". ChatGPT Images 2.6 launched on 4 November 2026; that date is summary only. The current models have **no identity-preservation dial**: `input_fidelity` exists only on the older gpt-image-1.5 and 1-mini, and gpt-image-2 and later always read their inputs at high fidelity. Transparent backgrounds are fully supported on 2.5 and 2.6 in the API; on gpt-image-2 they are still "preview". An edit takes up to 16 input images. OpenAI's own limitations section still says the models "may occasionally struggle to maintain visual consistency for recurring characters". OpenAI's prompting guide recommends **chaining** refinements (pass the previous output back in), while the 2026 research (§3) shows identity drifting with every chained edit. The practical answer is short chains inside one look, and a fresh start from the master image for every new look.

### Cited Findings

**Corrections to the earlier pass**

| Earlier claim | Status now | Evidence |
|---|---|---|
| ChatGPT Images 2.5 is current; "2.6" is probably a quiet update, unverified | **Wrong / superseded.** GPT-Image-2.6 Sunburst and Flare are on the official Models page and recommended for new integrations. ChatGPT Images 2.6 was released 4 Nov 2026. | Models page and image-generation guide (full page read); 4 Nov date from openai.com/index/introducing-images-2-6 (summary only) |
| `input_fidelity` high/low on gpt-image-1.5; gpt-image-2 "ignores" it | **Refined.** Not ignored: "For gpt-image-2, omit this parameter; the API doesn't allow changing it because the model processes every image input at high fidelity automatically." The 2.6 person-insertion example says "Omit input_fidelity from the edit request." | Image-generation guide, edit reference, prompting guide (full page read) |
| gpt-image-2 transparency is "preview" | **Correct**, and incomplete: 2.5 Sunburst and Flare, "including their 2026-09-08 snapshots, support opaque and transparent backgrounds", and both 2.6 models "support image generation, editing, and transparent backgrounds". | Edit reference, prompting guide (full page read) |
| Up to 16 input images | **Confirmed** for the GPT image models listed (to 2.5 and their snapshots, plus `chatgpt-image-latest`); each image png, webp or jpg under 50 MB. The parameter text did not yet name 2.6 explicitly. | Edit reference (full page read) |
| "Restart from the clean master, not the last output" | **Not OpenAI's advice.** OpenAI says to chain: "Pass the previous output as the next edit input, request one change, and repeat the details to preserve." Papers in §3 show chained drift, so the earlier advice stands as practice, but it is not vendor guidance. | Prompting guide (full page read); §3 papers |
| C2PA plus SynthID on OpenAI images | **Confirmed in developer docs**, with detail (see Provenance below). | Content provenance guide (full page read) |

**Current models and naming** [Official]
- The Models page lists four image models: "GPT-Image-2.6 Sunburst: Image generation and editing for detailed visual work"; "GPT-Image-2.6 Flare: Image generation and editing for fast iteration"; "GPT-Image-2.5 Sunburst: Our most capable model for image generation and editing"; "GPT-Image-2.5 Flare: Fast, high-quality everyday image generation". — [OpenAI Models](https://developers.openai.com/api/docs/models) (full page read, accessed 2026-11-17)
- From the image-generation guide: "GPT-Image-2.6 includes Sunburst for detailed visual work and Flare for fast iteration. Both models support complexity control, markup-guided edits, SVG output, and animated GIF output through the Image API." Also: "For new integrations, use GPT-Image-2.6 Sunburst or Flare." The same page's overview paragraph still names only the 2.5 models, a sign the docs were only partly updated after the launch. — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation) (full page read)
- The edit endpoint accepts the model names gpt-image-1-mini, gpt-image-1.5, gpt-image-2, gpt-image-2-2026-04-21, gpt-image-2.5-sunburst(-2026-09-08), gpt-image-2.5-flare(-2026-09-08), gpt-image-2.6-sunburst, gpt-image-2.6-flare and **chatgpt-image-latest**. "gpt-image-1 was shut down on October 23, 2026"; "dall-e-2", "dall-e-3": "This model was retired on May 12, 2026." — [API reference: images.edit](https://developers.openai.com/api/reference/python/resources/images/methods/edit) (full page read)
- Sunburst 2.6 pricing: image output $30 per 1M tokens, image input $8, text input $5. Endpoints include v1/images/generations and v1/images/edits. — [GPT-Image-2.6 Sunburst model page](https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst) (full page read)
- ChatGPT side (summary only): Images 2.6 released 4 Nov 2026 to ChatGPT and Codex "across all subscription tiers", claimed 50% faster. **Saved references** (upload a picture, name it, recall it with @name in a later chat) are a ChatGPT feature rolling out gradually. An early Arena read (5 Nov 2026) put both 2.6 models just behind their 2.5 versions. — [OpenAI: Introducing Images 2.6](https://openai.com/index/introducing-images-2-6/) (summary only); [BetaNews](https://betanews.com/article/chatgpt-images-gifs-faster-generation/) [Secondary, summary only]; [i-scoop](https://www.i-scoop.eu/chatgpt-images-2-6/) [Weak, summary only]
- The Help Center article on images in ChatGPT could not be read (bot check). The earlier pass's excerpts ("make the background transparent"; "Upload a photo and ask ChatGPT to save it as a reference") remain **summary only**. — [Images in ChatGPT](https://help.openai.com/en/articles/11084440-images-in-chatgpt)

**References, editing, identity** [Official, full page read]
- Edits can "Generate new images using other images as a reference" and "Edit parts of an image by uploading an image and mask". The guide's example combines 4 input images. — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- **Give each reference a role:** "Identify each input by number and purpose: subject, style, clothing, or background. Explain how the inputs should combine and which elements should move where." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Style transfer:** "Assign the reference image a specific role: its palette, texture, or visual medium. Describe the new subject separately." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Changes vs. constraints:** "For edits, say 'change only X' and list the details to preserve, such as identity, geometry, layout, lighting, or labels. State exclusions such as unwanted text, logos, or watermarks." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Chained iteration (OpenAI's position):** "Iterate deliberately. Pass the previous output as the next edit input, request one change, and repeat the details to preserve. References such as 'same style as before' can carry context, but restate critical constraints if the result drifts." For a sequence of edits, "check the final image as well as each intermediate result." Also: "If part of an image must remain pixel-identical, composite the approved edit into the original." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **OpenAI's character-consistency example (2.6 tab):** "Continue the story: Reuse each model's generated character image and describe a new scene. Repeat the appearance constraints so the character stays consistent." The example prompt has labelled blocks: `Character Consistency: - Same green hooded tunic - Same facial features, proportions, and color palette …` and `Constraints: - Do not redesign the character - No text - No watermarks`. The first image in the series used "Plain forest background to clearly showcase the character" at size 1024x1536. — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Identity on insertion into a new scene:** "Insert a person into a new scene while preserving their identity. Specify natural lighting, believable detail, body framing, gaze, and interaction with the scene. State which facial features and proportions must remain unchanged. Omit input_fidelity from the edit request." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Pose and framing:** "Instructions such as 'full body visible, feet included,' 'looking down at the open book,' or 'hands naturally gripping the handlebars' make the intended pose and action clearer." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Exact text:** "Put required wording in quotes and describe its position and typography. Spell unusual words or brand names letter by letter when needed. Ask for no extra text, then check spelling and legibility in the output." — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- **Complexity (2.6, API only):** "Lower complexity can suit focused edits, such as changing a background or a sign. Higher complexity can help with dense text, complex layouts… Higher complexity can increase latency and introduce unwanted changes." The default is high. — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- **Markup-guided edits:** a transparent PNG overlay with the same pixel size as the first input (circles, sketches). Per the API reference, markup "Cannot be combined with mask". The reference says "Supports GPT Image 2.5" while the guide says 2.5 and 2.6. — [API reference](https://developers.openai.com/api/reference/python/resources/images/methods/edit); [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- **Responses API multi-turn:** "Iteratively make high fidelity edits to images with prompting". An `action` parameter can force `generate` (new image) instead of editing one already in the conversation. — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)

**Transparency** [Official, full page read]
- "For transparent backgrounds, set background: 'transparent' and use output_format: 'png' or 'webp'." — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- "Request both an isolated subject in the prompt and background='transparent' in the API. Use PNG or WebP, preserve the returned alpha channel… A drawn checkerboard is not transparency. For subsequent edits, repeat the requirement to preserve the transparent background." Also: "For transparent PNG or WebP, check the decoded alpha channel." The cut-out example asks for "crisp silhouette, no halos/fringing". — [Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
- Transparency in the **ChatGPT app** (as opposed to the API) could not be checked (Help Center blocked).

**Sizes and quality** [Official, full page read]
- Recommended sizes are 1024x1024, 1536x1024 and 1024x1536. Sunburst and Flare also take custom WIDTHxHEIGHT, for example 1536x864. Width and height must be multiples of 16, the aspect ratio between 1:3 and 3:1, no edge over 3840 px, and the total between 655,360 and 8,294,400 pixels. "For GPT-Image-2.5, resolutions above 2560x1440 are experimental." Quality on 2.5 and 2.6 runs low, medium, high, xhigh, max or auto. — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- SVG output works on generations only: "The image edit endpoint does not support SVG output". — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)

**Official limitations** [Official, full page read]
- "Text Rendering: Although significantly improved, the model can still struggle with precise text placement and clarity. Consistency: While capable of producing consistent imagery, the model may occasionally struggle to maintain visual consistency for recurring characters or brand elements across multiple generations. Composition Control: … may have difficulty placing elements precisely in structured or layout-sensitive compositions." Also: "Complex prompts may take up to 2 minutes." — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- Moderation: the API has `moderation: auto | low`. A blocked request returns `moderation_blocked` with coarse categories such as "violence". — [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)

**Provenance** [Official, full page read]
- The checker covers C2PA Content Credentials ("Images and PDFs: Signed metadata with issuer and AI-use details") and SynthID ("Images and audio: A watermark embedded directly in supported media"). "Editing, converting, or sharing a file can remove its metadata. A SynthID watermark is part of the image or audio itself and may survive some transformations." A not_detected result is no proof either way: content may still be OpenAI's "if its metadata was stripped… its watermark was degraded". Checks run through `POST /v1/content_provenance_checks` or the web tool at openai.com/verify. "Visible watermarks and labels are separate from the provenance signals checked by the API." — [Content provenance](https://developers.openai.com/api/docs/guides/content-provenance)
- Real-person likeness (summary only): the 2.0 and 2.5 system cards say realistic imagery of real people in sensitive contexts violates OpenAI's usage policies, with safeguards at the prompt and image layers. No 2.6-specific or saved-reference likeness rule was found. — [ChatGPT Images 2.5 system card](https://deploymentsafety.openai.com/chatgpt-images-2-5) (summary only)

### Inferences
- **Build the Wardrobe prompt from OpenAI's own template.** Use labelled blocks: `Image 1 = identity master (subject)`, `Image 2 = style anchor (palette, texture, medium)`, `Image 3+ = outfit pieces (clothing)`. Then `Scene/pose: full body visible, feet included, neutral standing pose, camera at chest height`, then `Character Consistency:` (the fixed identity block: face, build, hair, every scar with side and position), then `Change only: <the new pieces>`, then `Constraints: do not redesign the character; no text; no watermarks; plain solid chroma-blue (or green) background, the same value every time, no floor shadow, no props`. Every element maps onto an official recommendation quoted above.
- **2:3 is native.** 1024x1536 is exactly 2:3, so the Wardrobe can ask for that size and drop the crop guesswork. For 16:9 places, 1536x864 is a documented custom size. For square cards, 1024x1024.
- **Keep the chroma screen for now.** API transparency is real on 2.5 and 2.6, but the author works in the ChatGPT app, where transparency could not be confirmed. The screen also gives a known white-balance target. If the author ever uses the API, `background: "transparent"` with png output and an alpha check could replace keying. The docs' own warnings (halos, fringing, painted checkerboards) are the things to check.
- **Chaining policy.** OpenAI recommends chaining, and research shows drift with each turn (§3). So: at most 2–3 narrow refinement turns on one look. Every new look starts in a fresh conversation from the master image, not from the previous look. When only one region must change (a new pauldron, say), the doc's "composite the approved edit into the original" is the cleanest identity guarantee: paste the changed region onto the approved image in the key-out script.
- **Saved references in ChatGPT 2.6** (summary only) suit a canonical knight master. Save the master once and call it by name. The saved image still has to be the clean master, never a later output.
- **Provenance:** the key-out and re-encode step strips C2PA (official: "converting… can remove its metadata"), while SynthID may survive. Disclosure has to be visible on the page (§6).

### Gaps
- The Help Center text on ChatGPT-app features (transparency, saved references, per-chat reference limits, edit selection) could not be read; it is summary only.
- No OpenAI statement found on how many images ChatGPT (as opposed to the API) accepts per message, or on likeness rules for saved references.
- The ChatGPT Images 2.6 system card was not found.

---

## 2. Midjourney V8.x: Edit Model, references, style

### Takeaway
Midjourney's own docs confirm the earlier pass's main claim, though I read them as search excerpts only (the docs host showed a bot check). **V8.2 has been the default since 24 July 2026.** Its **Edit Model replaces Omni Reference, Character Reference and Retexture**, takes **up to 4 reference images**, and works with V8.1 and V8.2. Omni Reference remains a single-image V7 feature, and the docs tell V8 users to use the Edit Model instead.

### Cited Findings
- [Official] "V8.2 released as the default version on July 24, 2026. It also features the new Edit Model, which replaces Omni Reference, Character Reference, and the Retexture tool." — [Midjourney docs: Version](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version) (summary only)
- [Official] The Edit Model lets you "Generate new images using up to 4 reference images (replacing Omni Reference and Character Reference)" and "is compatible with Midjourney versions 8.1 and 8.2." — [Midjourney docs: Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model) (summary only)
- [Official] Omni Reference page: "When using V8.X, use the Edit Model instead—our improved approach to editing and creating with reference images." Omni Reference is a V7 feature that takes a single image. — [Midjourney docs: Omni Reference](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference) (summary only)
- [Official] Character Reference "is a feature compatible with Midjourney and Niji version 6… replaced by Omni Reference in V7, and the Edit Model in V8.X." — [Midjourney docs](https://docs.midjourney.com/docs/character-reference) (summary only)
- [Official] Multi-character tip: "If certain features or attributes are getting mixed up between your characters, it can be helpful to combine your characters into a single reference image." — [Midjourney docs: Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model) (summary only)
- [Official] The V7 Global Personalization Profile is compatible with V8.2. The 8.2 notes say personalization "understands" a user's taste better, especially on profiles with many rating points. — [Midjourney: Version 8.2](https://updates.midjourney.com/version-8-2/) (summary only)
- [Weak] The Edit Model reportedly opened to everyone on 27 August 2026. Third-party guides disagree on whether `--oref` still runs on V8.x (routed through V7) or is unsupported in the V8 compatibility chart. — [ud.hk guide](https://www.ud.hk/en-US/resources/ai/midjourney-edit-model-guide-2026-10-02) (summary only); [AlphaSignal](https://alphasignal.ai/news/midjourney-s-v8-2-edit-model-merges-inpainting-references-and-instructions-into) (summary only)

### Inferences
- **Midjourney is the better tool for a shared painterly style** across portraits, places, cards and the map, through a fixed `--sref` code or moodboard plus the Edit Model's 4 references. Even so, a full Wardrobe look (knight + 3 pieces + style) already fills the 4 reference slots, whereas OpenAI takes 16 inputs. For the Wardrobe, ChatGPT stays the simpler choice.
- If two recurring characters ever share a picture, Midjourney's own advice is to make **one composite reference image** of both, rather than separate references.

### Gaps
- Moodboard and `--sref` behaviour in V8.2 is not confirmed from official text (only the V8.1 note, "moodboards and srefs are now super stable", via the earlier pass).
- No Midjourney policy text on likeness of real people was retrieved.
- No official statement on the Edit Model's identity fidelity compared with Omni Reference.

---

## 3. Research on identity consistency and drift: how it is measured and what holds

### Takeaway
2026 papers agree that **identity drifts with every chained edit, even when nothing is asked to change**. Drift is worst for **small subjects (full-body framing), multi-subject scenes and degraded inputs**. The usual measure is face-embedding cosine similarity to an enrolled identity (ArcFace-type). Story benchmarks add character-ID similarity, style similarity, character-count matching and a "copy-paste" check. The paper reporting the most identity-stable results argues for identity held **outside** the generator (a persistent identity layer or a LoRA) rather than in context, but it comes from a vendor that sells such a layer. Full-body knight images sit exactly in the measured weak spot.

### Cited Findings
- [Paper] **Persistent Identity Preservation** (Phota Labs, arXiv 2609.04151v2, 10 Sep 2026; vendor-authored: the authors sell "Phota Identity"):
  - "identity degradation becomes more pronounced under iterative edits, small subject scales, severe image degradation, and multi-subject composition", and "strong image quality and instruction following do not necessarily imply strong identity fidelity."
  - Iterative edits: "gpt-image-2 decreases from approximately 0.71 at the initial step to 0.53 after four edits, while nb2 decreases from 0.65 to 0.5". By face scale, gpt-image-2 falls from about 0.71 (large faces) to 0.56 (small faces), and nb2 from 0.70 to 0.49.
  - Metric: identity similarity is the cosine between the output's face embedding and an enrolled identity, plus a threshold "identity match rate" R(τ).
  - Its own stated limit: "Perceived identity… can depend on body shape and proportions, age-related characteristics, posture… particularly relevant for full-body, small-subject, and stylized imagery."
  - [arXiv 2609.04151](https://arxiv.org/html/2609.04151v2) (full page read)
- [Paper] **LME-Bench / MT-OPSD** (arXiv 2609.35611, Sept 2026): "existing editing models degrade rapidly under recursive editing". The cause is a train–test mismatch: models are trained on clean inputs but must condition on their own outputs. "even when instructed to reproduce the input image without modification, the model exhibits measurable drift at each turn". After a few turns: "high-frequency chromatic noise, structural fragmentation, or severe identity drift." The benchmark is 100 ten-turn sessions. — [arXiv 2609.35611](https://arxiv.org/html/2609.35611) (full page read, abstract and introduction)
- [Paper] **ViStoryBench** (arXiv 2505.24862v4; CVPR 2026): 80 multi-shot stories in 10 visual styles, with 12 human-validated automatic metrics.
  - Metrics include Character Identification Similarity (CIDS), style similarity (CSD), Onstage Character Count Matching ("models struggle to generate the correct number of onstage characters… superfluous additions (hallucinations) or omitted figures") and **Copy-Paste detection**, which flags models that reuse the reference instead of learning the character.
  - Findings: "Methods with high character consistency and high copy-paste score… often have lower diversity (e.g., GPT-4o)"; "the simple Copy-Paste Baseline achieves optimal results across numerous metrics. However, its alignment score is notably low."
  - The user study ranked Doubao, AIbrm, UNO and GPT-4o top for character consistency, using May 2025 commercial versions (now dated).
  - [arXiv 2505.24862](https://arxiv.org/html/2505.24862v4) (full page read)
- [Paper] A NeurIPS 2026 poster (GWScore) says common protocols score identity with DreamSim, which "can inadvertently conflate identity preservation with subject pose." — [NeurIPS 2026 poster](https://neurips.cc/virtual/2026/poster/149833) (summary only)
- [Paper] Other 2026 multi-turn benchmarks: MTEdit-Bench (100 eight-turn samples; instruction following, content consistency, quality drift) — [arXiv 2610.23751](https://arxiv.org/html/2610.23751) (summary only); AnchorEdit (10+ rounds, causal memory) — [arXiv 2606.11751](https://arxiv.org/html/2606.11751) (summary only).
- [Paper] The FLUX.1 Kontext paper's admission ("characters lose identity… with each edit"; degraded after six edits) is in the earlier pass — [arXiv 2506.15742](https://arxiv.org/pdf/2506.15742).

### Inferences
- **Which method holds identity best (evidence-weighted):**
  1. Identity held outside the generator: a trained LoRA, or a persistent identity layer (the paper's claim, conflict of interest noted).
  2. In-context reference with a **fresh start from the master** for each image.
  3. Chained edits.

  For a solo author in ChatGPT, (2) is the practical ceiling.
- **Full-body looks are the hard case.** Face scale is small in a 2:3 full-body image, and the paper measures the largest identity loss there. Two practical counters:
  - Make the **master a pair**: a full-body sheet plus a face close-up, both attached, with the close-up's role stated ("Image 1: face identity; Image 2: body, proportions, armour fit").
  - Judge identity on **body cues as well as the face**: silhouette, proportions, stance, scars. The paper notes face metrics miss exactly these.
- **A home-made drift check.** Keep the master and every filed look. Before filing, view the new look beside the master at phone thumbnail size and check a fixed list: face shape, hair, scars and their side, build, height ratio, silhouette. Optionally compute a style or identity similarity score locally. The benchmarks' "copy-paste" warning cuts both ways: a look that copies the master pose exactly is consistent but lifeless, so vary pose deliberately.
- **Multi-subject pictures drift most** (paper above; count errors in ViStoryBench). Keep companions out of Wardrobe and portrait images. Group scenes are where errors are most likely and need the most checking.

### Gaps
- No independent 2026 benchmark scores GPT-Image-2.5 or 2.6 against Midjourney V8.2 or Gemini on identity across a story; the Phota figure includes gpt-image-2.5 Sunburst, but its numbers were not given in the text.
- No study measures identity drift in **painted or stylised** characters specifically; the metrics are built for photographic faces.

---

## 4. Art direction primary sources and what a usable one-page style guide holds

### Takeaway
The primary sources point to the same contents for a short art bible:
- a **vision statement used as a filter** (Bourassa: a "razor"; Cammarano: "anything contrary gets thrown away");
- a few **finished visual targets**;
- **per-character colour symbolism** and a **repeating-motifs list** (HoloVista);
- **short character briefs** (age, build, relations, personality) before drawing (Pentiment);
- **framing conventions borrowed from the source tradition** (front or ¾ view; a fixed "north" camera);
- a **distance test** for patterns (BG3).

A sequel or new Book may "grow the characters up" but must "maintain the distinctive style" (Darkest Dungeon II).

### Cited Findings
- [Primary] **Darkest Dungeon**: Chris Bourassa's GDC 2016 talk describes "a steadfast commitment to a clearly articulated, externalized creative core", which guides art, audio and design and "serves as a razor to make the hard cuts", so that "smart creative choices let you play to your limitations as well as your strengths". — [GDC Vault: A Torch in the Dark](https://gdcvault.com/play/1023424/A-Torch-in-the-Dark) (full page read: abstract only; slides on media.gdcvault.com blocked)
- [Primary] **Darkest Dungeon II** (PC Gamer interview, 29 Oct 2020). Bourassa: "the most important thing above all is to maintain the distinctive style of the game, and only leverage technology… if they are enhancing that style or evolving it, not trampling on it", and "it was important to just try to even grow the characters up a little bit." On returning cast: "We don't want to wholesale bring back every single favorite monster, and every single favorite hero." — [PC Gamer](https://www.pcgamer.com/interview-darkest-dungeon-2s-new-3d-look-monsters-the-narrator-and-its-surprising-aspirational-spirit/) (full page read). Marielle Fox's GDC 2024 talk covers moving the 2D style into 3D "through a few failures". — [GDC Vault](https://gdcvault.com/play/1034192/Facing-Our-Failures-Creating-3D) (full page read: abstract only)
- [Primary] **Pentiment**: art director Hannah Kennedy's Game Developer deep dive (25 Jan 2023):
  - The main cast was designed first "to set the standard for the rest". For everyone else, art got "a short bio explaining their age and build, who they are related to within the town and a brief description of their personality". First passes had "no emotions or specific person gestures". The game has 157 rigged characters.
  - Designs were revised as the story grew: Father Thomas's "first pass (left) vs. final design (right)". Costume details became story: "Andreas and Bert's hats moving between characters over time… evolving into their own little conversations and cutscenes."
  - Source-tradition framing: "In the historical woodcuts we were referencing, people are almost always shown in front or ¾ view." She refused to scale characters for depth because it would "vary the weight of the character detail size against the fixed world". The camera almost always faces "north".
  - The finished art "was way too time-consuming to revise repeatedly", so scenes were greyboxed as "simple, uncolored roughs".
  - [Game Developer: Deep Dive, the art of Pentiment](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) (full page read)
- [Primary, via press] **Pentiment typography**, Josh Sawyer at GDC 2025: six custom fonts with Lettermatic (Peasant, Cursive, Humanist, Printed, Textura, Thread Puller) give each character a "typographic voice" reflecting class and culture. — [Game Developer, 27 Mar 2025](https://www.gamedeveloper.com/design/pentiment-director-explains-how-going-all-in-on-fonts-helped-elevate-the-medieval-detective-rpg-) (full page read)
- [Primary] **HoloVista** postmortem (31 Aug 2021): the co-directors made mood boards separately and then compared them. A "Repeating Objects/Motifs" document filled scenes with objects that reinforced themes. "Well-defined color symbolism helped the art team to create a distinct vibe for each character". The style guide "contained all the typefaces, patterns, and logos found in HoloVista's world… made… early on, and multiple departments… referred to it at every stage". — [Game Developer](https://www.gamedeveloper.com/design/postmortem-aconites-holovista) (full page read)
- [Secondary, practitioner] **Effective Art Directors** (Ben Cammarano, 20 Nov 2008): "Create a vision statement… Any ideas or discussions that come into play to support this statement are more likely to be recognized; anything contrary gets thrown away." "Visual targeting: … The concept is the idea. The visual target is what the EAD wants it to look like in the end." Finished targets should be "collected into… a style guide, art bible, or organized directory". — [Game Developer](https://www.gamedeveloper.com/business/effective-art-directors-gaming-s-something-something) (full page read)
- [Primary, via press] **Baldur's Gate 3** (PC Gamer, 5 Feb 2024), art director Alena Dubrovina: "Patterns and clothing designs now needed to work from both close-up and far away"; "three patterns which, while distinct up close, looked the same at distance". On armour: "The main thing is looking cool, and fitting in the game setting, and telling the story that it needs to tell." Impractical designs were cut, and new ideas got "a small test". — [PC Gamer](https://www.pcgamer.com/larians-art-director-on-the-outfits-of-baldurs-gate-3-and-why-making-them-fit-matters-but-the-main-thing-is-looking-cool/) (full page read)
- [Primary] **The Banner Saga** (Game Developer, 19 Feb 2014): art "hand-painted in Photoshop"; animation "rotoscoped and each frame is drawn by hand" in Flash. — [Road to the IGF](https://www.gamedeveloper.com/design/road-to-the-igf-stoic-s-i-the-banner-saga-i-) (full page read)
- [Primary] **Wildermyth** GDC 2022: techniques to make generated heroes "memorable, relatable, even iconic", and to avoid "breach of trust, acting out of character". — [GDC Vault](https://gdcvault.com/play/1027614/Independent-Games-Summit-Session-Getting) (full page read: abstract). Slide advice to "lean into charm", avoid sad faces and favour subtle neutral expressions — [slides PDF](https://media.gdcvault.com/GDC+2022/Speaker+Slides/GettingPlayersEmotionally_Austin_Nate.pdf) (summary only; host blocked).
- [Primary] **Shape language** (Patrick Faulwetter, GDC 2019) treats "culture" as "story" written in "architecture, customs, symbols, values", and builds shape languages from abstract shapes for "vehicles, costumes, architecture and environments". — [GDC Vault](https://gdcvault.com/play/1025897/Art-Direction-Bootcamp-Building-Worlds) (full page read: abstract)
- [Primary] **Single-image narrative key art**: the Elder Scrolls Online talk covers "compositional strategies for crafting a compelling narrative within a single image". — [GDC Vault: Illustrating Tamriel](https://gdcvault.com/play/1026041/Illustrating-Tamriel-Creating-Key-Art) (summary only)
- Hades and Disco Elysium: GDC Vault search surfaced no art-direction talk (Disco Elysium's talks are on writing); the earlier pass's interview material stands.

### Inferences
**A one-page style guide for the site**, synthesised from the sources above; each line shows its source.
1. **Vision line, used as a razor** (Bourassa, Cammarano): one sentence naming the tradition and the mood, for example "worn, hand-painted storybook realism, as if from an old book of hours; earned, not glamorous". Any picture that contradicts it is rejected, however good it looks.
2. **Visual targets** (Cammarano): one approved image per surface (portrait, 16:9 place, square card, map, full-body look). A new image is judged against its target, not against the last image.
3. **Palette by role, and colour per person** (HoloVista): ground, ink, light, Book accent, danger, rank metals; one symbolic colour per recurring character, used in their portrait background and nowhere else.
4. **Motifs list** (HoloVista): 5–10 repeating objects or emblems the prose has already shown (the spoiler rule); reuse them in places and cards.
5. **Character briefs before images** (Pentiment): age, build, relations, temperament, scars and side, in a few lines per person. These become the identity block in every prompt.
6. **Framing conventions** (Pentiment): front or ¾ view only; same eye height; no depth scaling of people; a fixed compass for the map and place pictures ("north is up, light from the west").
7. **Distance test** (BG3): every pattern, heraldic charge and card motif must still read at phone thumbnail size; two patterns that merge at that size become one.
8. **Change rule** (Darkest Dungeon II): a new Book may age, scar and re-equip the knight (grow him up), but never changes medium, light direction or rendering style.
9. **Near-miss gallery**: real failures pinned beside their targets (from the earlier pass).

### Gaps
- No GDC talk transcript is reachable; GDC Vault gives abstracts only, and the slide PDFs host was blocked.
- No primary source on Hades or Inkulinati art bibles beyond the press interviews cited in the earlier pass.

---

## 5. Gaps from the earlier pass: left/right and mirror errors, hands, in-image text; redesigns across sequels; costume arcs

### Takeaway
- **Left/right:** the 2026 evidence shows a systematic left/right bias. Models place or bind the first-mentioned thing on the left, and apply under-specified edits to a default side. That is the mechanism behind "scar on the wrong side". Image-to-image with a reference cuts the bias a lot for GPT-Image, but does not remove it.
- **Hands:** articulated anatomy remains a measured weak point in 2026 open models; no 2026 measurement for GPT-Image or Midjourney was found.
- **Text:** OpenAI still lists text placement as a limitation.
- **Redesigns:** game sources treat costume as accumulated history ("What happened in their past that manifests itself today?").

### Cited Findings
- [Paper] **Order-to-Space bias** (arXiv 2603.03714, 2026, ICML format):
  - "the first-mentioned entity tends to appear on the left, and under-specified edits are often applied to a default side"; in image-to-image, "models tend to attach the requested attribute or action to the left entity by default."
  - "when mention order contradicts grounding constraints, T2I correctness can drop from ~90% in Aligned to ~20% in Reverse." The authors trace it to "a strong first-mentioned-left prior in web-scale caption–image data".
  - Order-following (homogenization) scores: text-to-image GPT-Image 86.4, Midjourney v7 86.8, NanoBanana 81.0. In image-to-image, GPT-Image was **lowest at 35.4**, against 83.4 for Qwen-Image: "explicit visual grounding partially mitigates order-locking, though substantial bias remains for many models."
  - [arXiv 2603.03714](https://arxiv.org/html/2603.03714) (full page read)
- [Paper] Spatial benchmarks: SpatialBench-UC (200 prompts in 100 counterfactual left/right pairs) — [arXiv 2601.13462](https://www.arxiv.org/pdf/2601.13462) (summary only); "Everything in Its Place" (ICLR 2026) — [arXiv 2601.20354](https://arxiv.org/abs/2601.20354) (summary only).
- [Paper] **Hands and anatomy**: models "continue to produce anatomical artifacts on highly articulated region[s]". HAF-Bench has 500 prompts across five categories, including hand gestures, hand–object interaction and self-contact, scored by an anatomical error rate judged by Gemini-3-Pro-Preview. The baselines tested were FLUX and SDXL only. — [arXiv 2605.25759](https://arxiv.org/html/2605.25759) (full page read, 25 May 2026). An earlier dataset of 56,000 generated humans found hands the most frequent abnormality, then feet and heads — [AbHuman summary](https://chatpaper.com/paper/38681) (summary only, year unconfirmed).
- [Official] **Text**: "the model can still struggle with precise text placement and clarity". Fixes: quote exact text, spell it letter by letter, "Ask for no extra text, then check spelling." — [OpenAI guides](https://developers.openai.com/api/docs/guides/image-prompting) (full page read). A third-party test headlined "Perfect Text" for 2.6 — [PhotoWorkout](https://www.photoworkout.com/?p=223762) [Weak, summary only].
- [Primary, via summary] **Costume as history**: Victoria Tran (Kitfox), GDC 2019: "Where is your character from? What happened in their past that manifests itself today? … How can you tell their story?" Fashion is "Codified, meaningful, and symbolic"; "information-poor" game outfits "don't bring anything to the game." — [Game Developer, 14 Jul 2019](https://www.gamedeveloper.com/design/fashion-in-games-why-it-matters) (full page read)
- [Primary] Redesign during production: BioShock Infinite's character art went through "multiple directions" and "how we settled on our final direction for Elizabeth" — [GDC Vault: Change Is Good](https://gdcvault.com/play/1020238/Change-Is-Good-The-Importance) (full page read: abstract). Remedy's *Control* brought a professional costume designer into the character pipeline — [GDC Vault: Costume in Games](https://gdcvault.com/browse/gdc-19/play/1025997) (full page read: abstract). Pentiment's Father Thomas was redesigned as his story role grew — [Game Developer](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) (full page read).
- [Primary] Sequel continuity: Double Fine checked in with the original art director so *Costume Quest 2*'s characters did not drift from the first game — [Game Developer](https://www.gamedeveloper.com/business/the-chilling-tale-of-the-development-of-i-costume-quest-2-i-) (summary only). Darkest Dungeon II: "grow the characters up a little bit" while maintaining "the distinctive style" — [PC Gamer](https://www.pcgamer.com/interview-darkest-dungeon-2s-new-3d-look-monsters-the-narrator-and-its-surprising-aspirational-spirit/) (full page read).

### Inferences
- **Mirror and side errors: write sides out every time.** The bias research shows unspecified sides fall to a default. So every asymmetric mark names both the character's side and the viewer's side: "scar through his LEFT eyebrow (on the viewer's right in a front view)". Name the asymmetric items first in the identity block, because first-mentioned items tend toward the left. Add a QA step: horizontally flip a thumbnail of the master and of the new look. If the new look matches the *flipped* master better, it was mirrored. Never "fix" a mirrored look by flipping the file: heraldry, sword hand and buckles flip with it.
- **Hands:** pose hands simply (resting on a sword pommel, gripping a belt). Avoid interlaced fingers and hand–object contact in Wardrobe looks. Use OpenAI's phrasing ("hands naturally gripping…"). Check finger counts at full size before keying.
- **Text in images:** keep lettering off pictures entirely. Shields, banners and cards carry charges, not words. Card titles and ranks are HTML over the art, which also keeps them accessible.
- **Costume arc per Book (the redesign practice applied):** the identity block never changes. A short "history" line accumulates and is restated each time: wear, repairs, a scar shown in the prose, a piece taken from someone. Darkest Dungeon II's "grow them up" and Tran's "past that manifests today" are the brief. One new Book portrait per changed look; older ones stay in the gallery as the record.

### Gaps
- No 2026 study measures mirror-flip of reference identity marks (scars, heraldry) specifically; the left/right bias papers test object layout and role binding, not mirrored identity marks.
- No 2026 hand or text-accuracy benchmark covering GPT-Image-2.5 or 2.6, or Midjourney V8.2, was found.

---

## 6. AI-art disclosure and reader perception

### Takeaway
Controlled 2026 studies find that the "AI-generated" label itself lowers aesthetic ratings, even when viewers cannot tell the images apart. The bias arises during deliberate, reflective viewing, and **short interpretive text that helps viewers make meaning reduces it**. Labels on news lower perceived accuracy, but the broader effects are limited. One widely cited 2023 "no effect on short stories" preprint has been **withdrawn**.

### Cited Findings
- [Paper] Wang et al., *Frontiers in Psychology*, 3 June 2026:
  - Three experiments used only AI-made paintings and changed only the creator label. A pretest kept only images viewers could not pick out above chance.
  - The bias was "substantially larger under controlled processing (mean difference = 0.45) than under automatic processing (mean difference = 0.11)".
  - "providing interpretive semantic cues—brief textual descriptions that support meaning construction during controlled processing—significantly mitigated the bias against AI-generated art." Study 3 had N = 127 (67 with cues, 60 without).
  - [Frontiers](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1827956/full) (full page read)
- [Paper] News-article AI labels, survey experiment with a nationally representative probability sample (n = 3,861): labelling "reduces its perceived accuracy" and interest, but not policy support or general misinformation concern. "increasing the salience of AI use reduces the negative impact of AI labeling on perceived accuracy". — [arXiv 2506.16202 v2, 11 Feb 2026](https://arxiv.org/abs/2506.16202) (full page read: abstract page)
- [Paper, caution] The earlier "AI disclosure has no meaningful effect… for… short stories" (negative only for first-person poems) preprint is **withdrawn** (v2, 25 Jun 2024: "The current findings do not comprehensively and accurately reflect what the new data suggests"). Do not cite it. — [arXiv 2303.06217](https://arxiv.org/abs/2303.06217) (full page read)
- [Paper] HCII 2026 (Synart): 54 undergraduates; viewers without art training were more sensitive to the label. Interviews cite "emotional hollowness, intention denial, and authenticity distrust". — [Springer](https://link.springer.com/chapter/10.1007/978-3-032-30846-7_13) (summary only; host refused)
- [Paper] An EEG and eye-tracking study (2026) finds labels change evaluative processing rather than affect — [arXiv 2610.10182](https://arxiv.org/html/2610.10182) (summary only).
- [Official] Visible labels are separate from embedded provenance signals — [OpenAI content provenance](https://developers.openai.com/api/docs/guides/content-provenance) (full page read).

### Inferences
- **Disclose, and give the reader meaning alongside it.** Use one colophon line ("Pictures made by the author with AI image tools, from his own designs, prompts and choices; the words are his"). Give each picture a short caption tied to the prose: the scene or line it illustrates. The Frontiers result suggests such "interpretive semantic cues" are what reduce the penalty. The spoiler rule already requires every picture to follow something the page said, so the caption can simply quote or point to it.
- **Remove obvious AI tells before publishing:** hands, extra figures, garbled marks. Prior studies used artefacts as confounds, and readers do notice them.
- Embedded provenance does not survive the key-out pipeline (§1), so the visible line is the disclosure.

### Gaps
- No 2025–2026 study on **web-serial or illustrated-fiction readers** specifically; the evidence is from art, product and news contexts.
- No official Royal Road, Wattpad or AO3 AI-image policy text was retrieved in this pass.

---

## 7. Presenting a growing portrait gallery on a phone (new material)

### Takeaway
NN/g's mobile research says most people stop after 3–4 carousel frames and need visible cues that more exist. A per-Book portrait gallery that grows past about 5 looks should become a **thumbnail strip or list with direct access**, not a long swipe sequence.

### Cited Findings
- [Secondary, usability research] "most people stop after viewing 3–4 different pages in the carousel… users should be able to reach the last item in the carousel in 3–4 steps (i.e., taps or swipes). If you have a high number of items, use a list view instead and allow people to directly access any of the items." Dots are tiny and often unnoticed; cues placed over busy images have low contrast, especially outdoors; a partially visible next item is a strong cue. — [NN/g: Carousels on Mobile Devices (2018, updated 24 Jan 2024)](https://www.nngroup.com/articles/mobile-carousels/) (full page read)
- [Secondary] "Include 5 or fewer frames within the carousel… it's difficult for users to recognize topics they have already viewed when a set exceeds about five." Don't auto-forward unless the timing can be got right. — [NN/g: Carousel Usability (last reviewed 7 Aug 2026)](https://www.nngroup.com/articles/designing-effective-carousels/) (full page read)

### Inferences
- **Portrait history:** show the current Book's portrait large, then a row of small labelled thumbnails ("Book I", "Book II", …) for direct access, with the next one peeking at the edge. Use swipe as an extra, never the only way in. No auto-advance. Arrows and labels sit outside the painting, not on top of it.
- **The Wardrobe's looks** follow the same rule: a grid of thumbnails with the worn look marked, not a carousel.

### Gaps
- NN/g has no research specific to art galleries or serial fiction; the guidance is about general carousels.
