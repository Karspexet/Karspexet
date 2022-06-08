import * as Sentry from "@sentry/browser";
import { BrowserTracing } from "@sentry/tracing";

export function initSentry() {
  // @ts-expect-error
  if (import.meta.env.DEV) {
    return;
  }

  Sentry.init({
    dsn: "https://a2c447d27d42448e804317bef19ad89c@o991062.ingest.sentry.io/6418837",
    integrations: [new BrowserTracing()],

    // Set tracesSampleRate to 1.0 to capture 100% of transactions for performance monitoring.
    tracesSampleRate: 0.1,
  });

  // @ts-ignore
  window.Sentry = Sentry;

  // @ts-ignore
  window.triggerError = () => console.log(myUndefinedFunction());
}
