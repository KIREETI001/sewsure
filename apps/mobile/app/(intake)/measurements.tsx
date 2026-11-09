import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useRouter } from "expo-router";
import { isLocalJourney } from "@/api/localTransport";
import { prepareLocalProject } from "@/api/localJourney";
import { parseCmToMm } from "../../ui";
import { getApi } from "@/api/client";
import { BODY_CONSENT_VERSION, type IntakeRequest } from "@/api/types";
import {
  Body,
  Button,
  Chip,
  Heading,
  MockBadge,
  Notice,
  Row,
  Screen,
  TextField,
} from "@/components/plain";
import { t, type MessageKey } from "@/i18n";
import {
  BODY_SPECS,
  garmentSpecsFor,
  INSPIRATION_ONLY,
  type MeasurementSpec,
} from "@/intake/measurements";
import {
  buildMeasurementRecords,
  evaluateEntry,
  missingSpecs,
  mmToCm,
  type EntryStatus,
  unconfirmedSpecs,
} from "@/intake/validation";
import { inspirationFor, useIntakeStore } from "@/state/intakeStore";

const fieldLabel = (spec: MeasurementSpec) => t(`measure.field.${spec.key}` as MessageKey);

function MeasureField({ spec }: { spec: MeasurementSpec }) {
  const entry = useIntakeStore((s) => s.measurements[spec.key]);
  const setMeasurement = useIntakeStore((s) => s.setMeasurement);
  const status: EntryStatus = evaluateEntry(spec, entry);

  const write = (inputCm: string, confirmedAt: string | null) =>
    setMeasurement(spec.key, { inputCm, confirmedAt, origin: "user_entered" });

  // A clean value is confirmed when the user leaves the field. Any edit clears confirmation,
  // so a changed value is always reconfirmed.
  const onBlur = () => {
    if (status.state === "needs_review" && status.plausibility.level === "ok") {
      write(entry?.inputCm ?? "", new Date().toISOString());
    }
  };

  const valueCm = "mm" in status ? mmToCm(status.mm) : 0;
  const review = status.state === "needs_review" ? status : null;
  const warnMessage = (): string | null => {
    if (status.state === "invalid") {
      return t(status.reason === "not_positive" ? "measure.notPositive" : "measure.invalid");
    }
    const p =
      status.state === "blocked" || status.state === "needs_review" ? status.plausibility : null;
    if (!p || p.code === "ok") return null;
    const vars = { value: valueCm, suggested: p.suggestedCm ?? "" };
    if (spec.group === "body") return t("measure.doubleCheck");
    if (p.code === "out_of_range") return t("measure.outOfRange", vars);
    if (p.code === "maybe_missing_zero") return t("measure.maybeMissingZero", vars);
    if (p.code === "maybe_extra_zero") return t("measure.maybeExtraZero", vars);
    return t("measure.unusual", vars);
  };
  const message = warnMessage();
  const suggested =
    review?.plausibility.suggestedCm ??
    (status.state === "blocked" ? status.plausibility.suggestedCm : undefined);

  return (
    <>
      <TextField
        label={`${fieldLabel(spec)} (${t("common.cm")})`}
        hint={t("measure.hint")}
        keyboardType="decimal-pad"
        value={entry?.inputCm ?? ""}
        onChangeText={(v) => write(v, null)}
        onBlur={onBlur}
      />
      {message && (
        <Notice tone={status.state === "needs_review" ? "warn" : "error"}>
          <Body>{message}</Body>
          <Row>
            {suggested !== undefined && (
              <Button
                secondary
                label={t("measure.useSuggested", { suggested })}
                onPress={() => write(String(suggested), new Date().toISOString())}
              />
            )}
            {review && (
              <Button
                secondary
                label={t("measure.keep", { value: valueCm })}
                onPress={() => write(entry?.inputCm ?? "", new Date().toISOString())}
              />
            )}
          </Row>
        </Notice>
      )}
      {status.state === "confirmed" && (
        <Body muted accessibilityLabel={t("measure.confirmed", { value: valueCm })}>
          ✓ {t("measure.confirmed", { value: valueCm })}
        </Body>
      )}
    </>
  );
}

export default function MeasurementsScreen() {
  const router = useRouter();
  const local = isLocalJourney();
  const [targetCm, setTargetCm] = useState("45");
  const [placketCm, setPlacketCm] = useState("60");
  const [transformation, setTransformation] = useState<"crop" | "lengthen" | "other">("crop");
  const [localError, setLocalError] = useState(false);
  const draft = useIntakeStore();
  const { category, front, back, fit, skill, measurements, uploadStatus, guest } = draft;
  const inspiration = inspirationFor(draft.inspirationMode, draft.inspirationDraft);
  const bodyShared = draft.bodyConsentVersion !== null;
  const bodySpecs = bodyShared ? BODY_SPECS : [];
  const unconfirmedBody = unconfirmedSpecs(bodySpecs, measurements);

  const ideaOnly = category !== null && INSPIRATION_ONLY.includes(category);
  const garmentSpecs = category && !ideaOnly ? garmentSpecsFor(category) : [];
  const missing = missingSpecs(garmentSpecs, measurements);
  const [attempted, setAttempted] = useState(false);
  const target = parseCmToMm(targetCm);
  const placket = placketCm.trim() ? parseCmToMm(placketCm) : null;
  const readyLocal =
    category !== null &&
    !!front?.checked &&
    !!back?.checked &&
    fit !== null &&
    skill !== null &&
    missing.length === 0 &&
    target.status === "ok" &&
    (!placket || placket.status === "ok") &&
    inspiration !== null &&
    inspiration.kind !== "image";
  const journey = useMutation({
    mutationFn: async () => {
      if (!readyLocal || target.status !== "ok") throw new Error("Invalid synthetic inputs");
      return prepareLocalProject(
        draft,
        target.mm,
        placket?.status === "ok" ? placket.mm : null,
        transformation,
      );
    },
    onSuccess: (projectId) => router.push({ pathname: "/generating", params: { projectId } }),
    onError: () => setLocalError(true),
  });

  const prerequisitesMet =
    category !== null &&
    !!front &&
    !!back &&
    inspiration !== null &&
    fit !== null &&
    skill !== null;

  const upload = useMutation({
    mutationFn: () => {
      const request: IntakeRequest = {
        front_photo_uri: front?.uri ?? "",
        back_photo_uri: back?.uri ?? "",
        category: category as NonNullable<typeof category>,
        inspiration: inspiration as NonNullable<typeof inspiration>,
        fit_preference: fit as NonNullable<typeof fit>,
        skill_level: skill as NonNullable<typeof skill>,
        tools: draft.tools,
        extra_materials: draft.extraMaterials,
        measurements: buildMeasurementRecords([...garmentSpecs, ...bodySpecs], measurements),
        body_consent_version: draft.bodyConsentVersion,
      };
      return getApi().uploadIntake(request);
    },
    onMutate: () => draft.patch({ uploadStatus: "uploading" }),
    onSuccess: (res) => draft.patch({ uploadStatus: "uploaded", uploadProvenance: res.provenance }),
    // The draft is untouched on failure: nothing the user typed is lost.
    onError: () => draft.patch({ uploadStatus: "failed" }),
  });

  const onUpload = () => {
    setAttempted(true);
    if (missing.length === 0 && unconfirmedBody.length === 0 && prerequisitesMet) upload.mutate();
  };

  const mockUpload = uploadStatus === "uploaded" && draft.uploadProvenance === "mock";
  const statusKey: MessageKey = guest
    ? "measure.draft.guest"
    : uploadStatus === "uploaded"
      ? mockUpload
        ? "measure.draft.mockUploaded"
        : "measure.draft.uploaded"
      : uploadStatus === "uploading"
        ? "measure.draft.uploading"
        : uploadStatus === "failed"
          ? "measure.draft.failed"
          : "measure.draft.notUploaded";

  return (
    <Screen>
      {local && (
        <Notice>
          <Body>{t("local.notice")}</Body>
        </Notice>
      )}
      <Body muted>{t("measure.intro")}</Body>
      <Row>
        <Body accessibilityLabel={t(statusKey)}>
          {`${uploadStatus === "uploaded" && !guest && !mockUpload ? "✓" : "○"} ${t(statusKey)}`}
        </Body>
        {uploadStatus === "uploaded" && !guest && draft.uploadProvenance === "mock" && (
          <MockBadge />
        )}
      </Row>

      {!prerequisitesMet && (
        <Notice>
          <Body>
            {t(category && front && back ? "measure.needsInspiration" : "measure.needsPhotos")}
          </Body>
        </Notice>
      )}

      <Heading>{t("measure.garmentHeading")}</Heading>
      {ideaOnly && (
        <Notice tone="info">
          <Body>{t("capture.category.ideaOnly")}</Body>
        </Notice>
      )}
      {garmentSpecs.map((spec) => (
        <MeasureField key={spec.key} spec={spec} />
      ))}

      {!local && <Heading>{t("measure.bodyHeading")}</Heading>}
      {!local && <Body muted>{t("measure.bodyConsent")}</Body>}
      {!local && (
        <Chip
          role="checkbox"
          label={t("measure.bodyOptIn")}
          selected={bodyShared}
          onPress={() =>
            draft.patch({ bodyConsentVersion: bodyShared ? null : BODY_CONSENT_VERSION })
          }
        />
      )}
      {!local && bodySpecs.map((spec) => <MeasureField key={spec.key} spec={spec} />)}
      {local && (
        <>
          <Row>
            {(["crop", "lengthen", "other"] as const).map((value) => (
              <Chip
                key={value}
                label={t(`local.${value}`)}
                selected={transformation === value}
                onPress={() => setTransformation(value)}
              />
            ))}
          </Row>
          <TextField
            label={t("local.target")}
            keyboardType="decimal-pad"
            value={targetCm}
            onChangeText={setTargetCm}
          />
          {category === "shirt" && (
            <>
              <TextField
                label={t("local.placket")}
                keyboardType="decimal-pad"
                value={placketCm}
                onChangeText={setPlacketCm}
              />
              <Body muted>{t("local.placketHint")}</Body>
            </>
          )}
          {inspiration?.kind === "image" && <Body>{t("local.textOnly")}</Body>}
          {!readyLocal && <Body>{t("local.invalid")}</Body>}
          {localError && (
            <Notice tone="error">
              <Body>{t("local.failed")}</Body>
            </Notice>
          )}
          <Button
            label={t(journey.isPending ? "local.working" : "local.continue")}
            disabled={!readyLocal || journey.isPending}
            onPress={() => {
              setLocalError(false);
              journey.mutate();
            }}
          />
        </>
      )}
      {attempted && unconfirmedBody.length > 0 && (
        <Notice>
          <Body>
            {t("measure.unconfirmedBody", { fields: unconfirmedBody.map(fieldLabel).join(", ") })}
          </Body>
        </Notice>
      )}

      {attempted && missing.length > 0 && (
        <Notice>
          <Body>{t("measure.missing", { fields: missing.map(fieldLabel).join(", ") })}</Body>
        </Notice>
      )}
      {upload.isError && (
        <Notice tone="error">
          <Body>{t("measure.draft.failed")}</Body>
        </Notice>
      )}

      {!guest && (
        <Button
          label={t(uploadStatus === "failed" ? "measure.uploadRetry" : "measure.upload")}
          disabled={uploadStatus === "uploading" || uploadStatus === "uploaded"}
          onPress={onUpload}
        />
      )}
    </Screen>
  );
}
