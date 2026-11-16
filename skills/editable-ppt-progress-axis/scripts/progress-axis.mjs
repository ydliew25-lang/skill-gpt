const NAME_PREFIX = "进度轴组件·";

const PALETTES = {
  light: { text: "#5C665C", track: "#DAD1C3", done: "#82968A", active: "#904631" },
  dark: { text: "#B7CCC1", track: "#45635D", done: "#9AB2A5", active: "#ECC6A6" },
};

const LAYOUT = {
  left: 72, right: 72, gap: 12,
  labelTop: 9, labelHeight: 22, fontSize: 15,
  trackTop: 34, trackHeight: 1.5, fillTop: 33, fillHeight: 2.5,
};

const noLine = { fill: "none", width: 0 };

/** Map one-based presentation positions to a chapter or a neutral overview. */
export function createProgressPlan({ slideCount, sections, overviewPages = [] }) {
  if (!Number.isInteger(slideCount) || slideCount < 1) {
    throw new RangeError("slideCount must be a positive integer.");
  }
  if (!Array.isArray(sections) || sections.length === 0) {
    throw new TypeError("At least one section is required.");
  }

  const pages = Array(slideCount).fill(undefined);
  function assign(page, state) {
    if (!Number.isInteger(page) || page < 1 || page > slideCount) {
      throw new RangeError(`Page ${page} falls outside the presentation.`);
    }
    if (pages[page - 1] !== undefined) {
      throw new RangeError(`Page ${page} appears more than once in the plan.`);
    }
    pages[page - 1] = state;
  }

  for (const page of overviewPages) assign(page, null);
  const titles = new Set();
  let precedingLast = 0;
  const normalized = sections.map((section, index) => {
    const title = typeof section.title === "string" ? section.title.trim() : "";
    if (!title || titles.has(title)) {
      throw new TypeError("Every section must have a unique, nonempty title.");
    }
    const { first, last } = section;
    if (!Number.isInteger(first) || !Number.isInteger(last) ||
        first <= precedingLast || first > last || last > slideCount) {
      throw new RangeError(`Invalid or out-of-order range for "${title}": ${first}–${last}.`);
    }
    titles.add(title);
    precedingLast = last;
    for (let page = first; page <= last; page++) {
      assign(page, { section: index, fraction: (page - first + 1) / (last - first + 1) });
    }
    return { ...section, title };
  });

  const missing = pages.indexOf(undefined);
  if (missing !== -1) {
    throw new RangeError(`Page ${missing + 1} is missing from the plan.`);
  }
  return { sections: normalized, pages };
}

function rectangle(slide, name, left, top, width, height, fill) {
  slide.shapes.add({
    name, geometry: "rect", position: { left, top, width, height }, fill, line: noLine,
  });
}

/** Draw or refresh the navigation on an Artifact Tool-compatible slide. */
export function addProgressAxis(slide, plan, page, options = {}) {
  if (!Number.isInteger(page) || page < 1 || page > plan.pages.length) {
    throw new RangeError(`Invalid page: ${page}.`);
  }
  const width = options.width ?? slide.frame?.width ?? 1280;
  if (!Number.isFinite(width) || width <= 0) {
    throw new RangeError("The slide width must be positive.");
  }

  const defaults = Object.fromEntries(Object.entries(LAYOUT).map(([key, number]) => [
    key, number * width / 1280,
  ]));
  const layout = { ...defaults, ...options.layout };
  for (const key of Object.keys(LAYOUT)) {
    if (!Number.isFinite(layout[key]) || layout[key] < 0) {
      throw new RangeError(`Invalid progress-axis geometry: ${key}.`);
    }
  }
  const { left, right, gap, labelTop, labelHeight, fontSize,
          trackTop, trackHeight, fillTop, fillHeight } = layout;
  const segment = (width - left - right - gap * (plan.sections.length - 1)) /
    plan.sections.length;
  const bottom = Math.max(labelTop + labelHeight, trackTop + trackHeight, fillTop + fillHeight);
  if (segment <= 0 || fontSize === 0 || labelHeight === 0 || trackHeight === 0 ||
      fillHeight === 0 || labelTop + labelHeight > Math.min(trackTop, fillTop) ||
      bottom > (options.clearance ?? Infinity)) {
    throw new RangeError("The progress axis does not fit the reserved header area.");
  }

  const palette = { ...PALETTES[options.dark ? "dark" : "light"], ...options.palette };
  const state = plan.pages[page - 1];
  for (const shape of [...slide.shapes.items]) {
    if (shape.name?.startsWith(NAME_PREFIX)) shape.delete();
  }

  for (const [index, section] of plan.sections.entries()) {
    const x = left + index * (segment + gap);
    const active = index === state?.section;
    const completed = state !== null && index < state.section;
    const label = slide.shapes.add({
      name: `${NAME_PREFIX}章名·${section.title}`, geometry: "textbox",
      position: { left: x, top: labelTop, width: segment, height: labelHeight },
      fill: "none", line: noLine,
    });
    label.text = section.title;
    label.text.style = {
      typeface: options.typeface ?? "Noto Sans CJK SC", fontSize,
      bold: active, color: active ? palette.active : palette.text,
      insets: 0, alignment: "left", verticalAlignment: "middle",
      wrap: "none", autoFit: "none", lineSpacing: 1.12,
    };
    rectangle(slide, `${NAME_PREFIX}底线·${section.title}`,
      x, trackTop, segment, trackHeight, palette.track);
    if (active || completed) {
      rectangle(slide, `${NAME_PREFIX}填充·${section.title}`,
        x, fillTop, segment * (active ? state.fraction : 1), fillHeight,
        active ? palette.active : palette.done);
    }
  }
}
