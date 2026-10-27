import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { getApi } from "@/api/client";
import type { IntakeRequest } from "@/api/types";
import { Body, Button, Heading, Notice, Row, Screen, TextField } from "@/components/plain";
import { t, type MessageKey } from "@/i18n";
import { BODY_SPECS, garmentSpecsFor, type MeasurementSpec } from "@/intake/measurements";
import {
  buildMeasurementRecords,
  evaluateEntry,
  missingSpecs,
  mmToCm,
  type EntryStatus,
} from "@/intake/validation";
import { useIntakeStore } from "@/state/intakeStore";

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
        <Body muted>✓ {t("measure.confirmed", { value: valueCm })}</Body>
      )}
    </>
  );
}

export default function MeasurementsScreen() {
  const draft = useIntakeStore();
  const { category, front, back, inspiration, fit, skill, measurements, uploadStatus, guest } =
    draft;

  const garmentSpecs = category ? garmentSpecsFor(category) : [];
  const missing = missingSpecs(garmentSpecs, measurements);
  const [attempted, setAttempted] = useState(false);

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
        measurements: buildMeasurementRecords([...garmentSpecs, ...BODY_SPECS], measurements),
      };
      return getApi().uploadIntake(request);
    },
    onMutate: () => draft.patch({ uploadStatus: "uploading" }),
    onSuccess: () => draft.patch({ uploadStatus: "uploaded" }),
    // The draft is untouched on failure: nothing the user typed is lost.
    onError: () => draft.patch({ uploadStatus: "failed" }),
  });

  const onUpload = () => {
    setAttempted(true);
    if (missing.length === 0 && prerequisitesMet) upload.mutate();
  };

  const statusKey: MessageKey = guest
    ? "measure.draft.guest"
    : uploadStatus === "uploaded"
      ? "measure.draft.uploaded"
      : uploadStatus === "uploading"
        ? "measure.draft.uploading"
        : uploadStatus === "failed"
          ? "measure.draft.failed"
          : "measure.draft.notUploaded";

  return (
    <Screen>
      <Body muted>{t("measure.intro")}</Body>
      <Body>{`${uploadStatus === "uploaded" && !guest ? "✓" : "○"} ${t(statusKey)}`}</Body>

      {!prerequisitesMet && (
        <Notice>
          <Body>
            {t(category && front && back ? "measure.needsInspiration" : "measure.needsPhotos")}
          </Body>
        </Notice>
      )}

      <Heading>{t("measure.garmentHeading")}</Heading>
      {garmentSpecs.map((spec) => (
        <MeasureField key={spec.key} spec={spec} />
      ))}

      <Heading>{t("measure.bodyHeading")}</Heading>
      <Body muted>{t("measure.bodyConsent")}</Body>
      {BODY_SPECS.map((spec) => (
        <MeasureField key={spec.key} spec={spec} />
      ))}

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
