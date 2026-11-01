import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, ScrollView, View } from "react-native";
import { getStudioApi, setMockScenario } from "@/api/studio";
import type { InspirationInput } from "@/api/types";
import { t, type MessageKey } from "@/i18n";
import { inspirationFor, useIntakeStore } from "@/state/intakeStore";
import { newIdempotencyKey, useStudioStore } from "@/state/studioStore";
import { toShownError, type ShownError } from "@/studio/errors";
import { isScenarioName } from "@/studio/scenarios";
import type { Job } from "@/studio/types";
import { Button, MockBadge, Text, ThemeProvider } from "../../ui";

const POLL_MS = 1500;
const TIMEOUT_MS = 90_000;
const MAX_POLL_FAILURES = 3;
const DEMO_INSPIRATION: InspirationInput = { kind: "text", text: "Demo: a cropped version" };

type Phase =
  | { kind: "starting" }
  | { kind: "running"; job: Job }
  | { kind: "failed"; error: ShownError }
  | { kind: "timeout" };

const summary = (i: InspirationInput | null, demo: boolean): string => {
  if (demo) return t("studio.generating.demoRequest");
  if (!i) return "";
  if (i.kind === "image") return t("studio.generating.requestImage");
  return i.kind === "text" ? i.text : i.prompt;
};

export default function GeneratingScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ scenario?: string; projectId?: string }>();
  const api = getStudioApi();
  const mode = useIntakeStore((s) => s.inspirationMode);
  const draft = useIntakeStore((s) => s.inspirationDraft);
  const real = inspirationFor(mode, draft);
  const inspiration = real ?? (api.mode === "mock" ? DEMO_INSPIRATION : null);

  const [phase, setPhase] = useState<Phase>({ kind: "starting" });
  const [attempt, setAttempt] = useState(0);
  const [resume, setResume] = useState(0);
  const jobRef = useRef<string | null>(null);

  useEffect(() => {
    if (!inspiration) return;
    let cancelled = false;
    const deadline = Date.now() + TIMEOUT_MS;
    const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

    const run = async () => {
      let jobId = jobRef.current;
      if (!jobId) {
        if (api.mode === "mock" && isScenarioName(params.scenario) && attempt === 0) {
          setMockScenario(params.scenario);
        }
        const projectId = params.projectId ?? "mock-project";
        const key = newIdempotencyKey();
        useStudioStore.getState().startAttempt(projectId, key);
        try {
          const started = await api.generate(projectId, { inspiration }, { idempotencyKey: key });
          if (cancelled) return;
          jobId = started.data.job_id;
          jobRef.current = jobId;
          useStudioStore.getState().setJob(jobId);
          setPhase({ kind: "running", job: started.data });
        } catch (e) {
          if (!cancelled)
            setPhase({
              kind: "failed",
              error: toShownError(e, t("studio.generating.failed.network")),
            });
          return;
        }
      }
      let failures = 0;
      while (!cancelled) {
        if (Date.now() > deadline) {
          setPhase({ kind: "timeout" });
          return;
        }
        await sleep(POLL_MS);
        if (cancelled) return;
        try {
          const { data: job } = await api.getJob(jobId);
          failures = 0;
          if (cancelled) return;
          if (job.state === "failed") {
            const e = job.error;
            setPhase({
              kind: "failed",
              error: {
                code: e?.code ?? "JOB_FAILED",
                message: e?.message ?? t("studio.generating.failed.network"),
                recoverable: e?.recoverable ?? true,
                retryAfterS: e?.retry_after_s ?? null,
              },
            });
            return;
          }
          if (job.state === "complete") {
            router.replace("/results");
            return;
          }
          setPhase({ kind: "running", job });
        } catch (e) {
          failures += 1;
          if (failures >= MAX_POLL_FAILURES) {
            if (!cancelled)
              setPhase({
                kind: "failed",
                error: toShownError(e, t("studio.generating.failed.network")),
              });
            return;
          }
        }
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt, resume]);

  const retry = () => {
    jobRef.current = null;
    setPhase({ kind: "starting" });
    setAttempt((n) => n + 1);
  };
  const keepWaiting = () => {
    setPhase({ kind: "starting" });
    setResume((n) => n + 1);
  };

  const stage =
    phase.kind === "running"
      ? t(`studio.generating.stage.${phase.job.stage ?? "waiting"}` as MessageKey)
      : t("studio.generating.starting");

  return (
    <ThemeProvider>
      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {api.mode === "mock" ? <MockBadge /> : null}
        <Text variant="title" accessibilityRole="header">
          {t("studio.generating.title")}
        </Text>
        <Text>{t("studio.generating.intro")}</Text>
        <Text tone="secondary">{t("studio.generating.saved")}</Text>
        {inspiration ? (
          <Text>
            {t("studio.generating.yourRequest", { summary: summary(inspiration, !real) })}
          </Text>
        ) : (
          <>
            <Text tone="danger">{`! ${t("studio.generating.noRequest")}`}</Text>
            <Button
              label={t("studio.generating.editRequest")}
              onPress={() => router.replace("/inspiration")}
            />
          </>
        )}
        {inspiration && (phase.kind === "starting" || phase.kind === "running") ? (
          <View
            accessible
            accessibilityRole="progressbar"
            accessibilityLabel={stage}
            style={{ gap: 8 }}
          >
            <ActivityIndicator />
            <Text>{t("studio.generating.stage", { stage })}</Text>
          </View>
        ) : null}
        {phase.kind === "timeout" ? (
          <View style={{ gap: 8 }}>
            <Text variant="heading" accessibilityRole="header">
              {t("studio.generating.timeout.title")}
            </Text>
            <Text>{t("studio.generating.timeout.body")}</Text>
            <Button
              label={t("studio.generating.keepWaiting")}
              variant="secondary"
              onPress={keepWaiting}
            />
            <Button label={t("common.retry")} onPress={retry} />
          </View>
        ) : null}
        {phase.kind === "failed" ? (
          <View style={{ gap: 8 }}>
            <Text variant="heading" accessibilityRole="header">
              {t("studio.generating.failed.title")}
            </Text>
            <Text tone="danger" accessibilityRole="alert">{`! ${phase.error.message}`}</Text>
            {phase.error.retryAfterS ? (
              <Text tone="secondary">
                {t("studio.generating.retryAfter", { seconds: phase.error.retryAfterS })}
              </Text>
            ) : null}
            {phase.error.recoverable ? (
              <Button label={t("common.retry")} onPress={retry} />
            ) : (
              <>
                <Text>{t("studio.generating.notRecoverable")}</Text>
                <Button
                  label={t("studio.generating.editRequest")}
                  onPress={() => router.replace("/inspiration")}
                />
              </>
            )}
          </View>
        ) : null}
      </ScrollView>
    </ThemeProvider>
  );
}
