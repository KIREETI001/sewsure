/* global afterEach, jest, it, expect */
const fs = require("node:fs");
const configure = require("../app.config");

const originalMode = process.env.NODE_ENV;
const originalQa = process.env.SEWSURE_QA_ROUTES;
afterEach(() => {
  jest.restoreAllMocks();
  if (originalMode === undefined) delete process.env.NODE_ENV;
  else process.env.NODE_ENV = originalMode;
  if (originalQa === undefined) delete process.env.SEWSURE_QA_ROUTES;
  else process.env.SEWSURE_QA_ROUTES = originalQa;
});

it.each(["production", "test", undefined])(
  "blocks leftover QA routes in %s even with QA enabled",
  (mode) => {
    jest.spyOn(fs, "existsSync").mockReturnValue(true);
    if (mode === undefined) delete process.env.NODE_ENV;
    else process.env.NODE_ENV = mode;
    process.env.SEWSURE_QA_ROUTES = "1";
    expect(() => configure({ config: {} })).toThrow("qa:remove");
  },
);

it("requires explicit QA opt-in in development", () => {
  jest.spyOn(fs, "existsSync").mockReturnValue(true);
  process.env.NODE_ENV = "development";
  delete process.env.SEWSURE_QA_ROUTES;
  expect(() => configure({ config: {} })).toThrow("qa:remove");
  process.env.SEWSURE_QA_ROUTES = "1";
  const config = { scheme: "sewsure" };
  expect(configure({ config })).toBe(config);
});

it("leaves production config unchanged without generated routes", () => {
  jest.spyOn(fs, "existsSync").mockReturnValue(false);
  process.env.NODE_ENV = "production";
  process.env.SEWSURE_QA_ROUTES = "1";
  const config = { plugins: ["expo-router"] };
  expect(configure({ config })).toBe(config);
});
