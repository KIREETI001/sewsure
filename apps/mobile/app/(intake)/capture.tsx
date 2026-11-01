import { useQuery } from "@tanstack/react-query";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Image, Linking } from "react-native";
import { getApi } from "@/api/client";
import type { GarmentCategory } from "@/api/types";
import { Body, Button, Chip, Heading, MockBadge, Notice, Row, Screen } from "@/components/plain";
import { t, type MessageKey } from "@/i18n";
import { INSPIRATION_ONLY } from "@/intake/measurements";
import { checkPhotoBasics } from "@/intake/validation";
import { useIntakeStore, type PhotoDraft } from "@/state/intakeStore";

const CATEGORIES: GarmentCategory[] = ["shirt", "tee", "jacket", "trousers", "skirt", "dress"];
type Side = "front" | "back";

const categoryLabel = (c: GarmentCategory) => t(`capture.category.${c}` as MessageKey);

function PhotoSlot({ side }: { side: Side }) {
  const photo = useIntakeStore((s) => s[side]);
  const patch = useIntakeStore((s) => s.patch);
  const [denied, setDenied] = useState(false);
  const [failed, setFailed] = useState(false);
  const sideLabel = t(side === "front" ? "capture.front" : "capture.back");

  const pick = async (source: "camera" | "library") => {
    setFailed(false);
    try {
      if (source === "camera") {
        const perm = await ImagePicker.requestCameraPermissionsAsync();
        if (!perm.granted) {
          setDenied(true);
          return;
        }
      }
      setDenied(false);
      const launch =
        source === "camera" ? ImagePicker.launchCameraAsync : ImagePicker.launchImageLibraryAsync;
      const result = await launch({ mediaTypes: ["images"], quality: 0.8 });
      if (result.canceled) return;
      const asset = result.assets[0];
      if (!asset) return;
      patch({
        [side]: { uri: asset.uri, width: asset.width, height: asset.height, checked: false },
      });
    } catch {
      setFailed(true);
    }
  };

  const setChecked = (checked: boolean) => {
    if (photo) patch({ [side]: { ...photo, checked } satisfies PhotoDraft });
  };

  const lowRes = photo ? checkPhotoBasics(photo).warnings.includes("low_resolution") : false;

  return (
    <>
      <Heading>{sideLabel}</Heading>
      {photo ? (
        <>
          <Image
            source={{ uri: photo.uri }}
            accessibilityLabel={t("capture.photoAlt", { side: sideLabel })}
            style={{ width: "100%", aspectRatio: 1, borderRadius: 8 }}
            resizeMode="contain"
          />
          {lowRes && (
            <Notice>
              <Body>{t("capture.lowRes")}</Body>
            </Notice>
          )}
          <Body>{t("capture.check.heading")}</Body>
          <Chip
            role="checkbox"
            label={t("capture.check.all")}
            selected={photo.checked}
            onPress={() => setChecked(!photo.checked)}
          />
          <Row>
            <Button secondary label={t("capture.retake")} onPress={() => pick("camera")} />
            <Button
              secondary
              label={t("capture.remove")}
              accessibilityLabel={`${t("capture.remove")} ${sideLabel}`}
              onPress={() => patch({ [side]: null })}
            />
          </Row>
        </>
      ) : (
        <>
          <Body muted>{t("capture.empty", { side: sideLabel.toLowerCase() })}</Body>
          <Row>
            <Button
              label={t("capture.take")}
              accessibilityLabel={`${t("capture.take")}: ${sideLabel}`}
              onPress={() => pick("camera")}
            />
            <Button
              secondary
              label={t("capture.library")}
              accessibilityLabel={`${t("capture.library")}: ${sideLabel}`}
              onPress={() => pick("library")}
            />
          </Row>
        </>
      )}
      {denied && (
        <Notice>
          <Body>{t("capture.permissionDenied")}</Body>
          <Button
            secondary
            label={t("capture.openSettings")}
            onPress={() => Linking.openSettings()}
          />
        </Notice>
      )}
      {failed && (
        <Notice tone="error">
          <Body>{t("capture.pickFailed")}</Body>
        </Notice>
      )}
    </>
  );
}

export default function CaptureScreen() {
  const router = useRouter();
  const { front, back, category, patch } = useIntakeStore();

  const suggestion = useQuery({
    queryKey: ["suggestCategory", front?.uri],
    queryFn: () => getApi().suggestCategory(front?.uri ?? ""),
    enabled: front !== null,
  });

  const photosReady = !!front?.checked && !!back?.checked;
  const canContinue = photosReady && category !== null;

  return (
    <Screen>
      <Heading>{t("capture.guide.heading")}</Heading>
      <Body>{t("capture.guide.flat")}</Body>
      <Body>{t("capture.guide.light")}</Body>
      <Body>{t("capture.guide.sharp")}</Body>

      <PhotoSlot side="front" />
      <PhotoSlot side="back" />
      {front && back && !photosReady && (
        <Notice>
          <Body>{t("capture.checkNeeded")}</Body>
        </Notice>
      )}

      <Heading>{t("capture.category.heading")}</Heading>
      {suggestion.data && (
        <Row>
          <Body>
            {t("capture.category.suggested", {
              category: categoryLabel(suggestion.data.data.category),
            })}
          </Body>
          {suggestion.data.provenance === "mock" && <MockBadge />}
          <Button
            secondary
            label={t("capture.category.use")}
            onPress={() => patch({ category: suggestion.data.data.category })}
          />
        </Row>
      )}
      <Row>
        {CATEGORIES.map((c) => (
          <Chip
            key={c}
            label={categoryLabel(c)}
            selected={category === c}
            onPress={() => patch({ category: c })}
          />
        ))}
      </Row>
      {category === null && <Body muted>{t("capture.category.needed")}</Body>}
      {category !== null && INSPIRATION_ONLY.includes(category) && (
        <Notice tone="info">
          <Body>{t("capture.category.ideaOnly")}</Body>
        </Notice>
      )}
      {category === "tee" && <Body muted>{t("capture.category.teeNote")}</Body>}

      <Button
        label={t("common.continue")}
        disabled={!canContinue}
        onPress={() => router.push("/(intake)/inspiration")}
      />
    </Screen>
  );
}
