interface BackRouter {
  canGoBack: () => boolean;
  back: () => void;
  replace: (href: "/") => void;
}

/** After a deep link there is no history, so fall back to the app's start screen. */
export const goBack = (router: BackRouter): void => {
  if (router.canGoBack()) router.back();
  else router.replace("/");
};
