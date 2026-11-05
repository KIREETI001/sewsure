import { useMutation } from "@tanstack/react-query";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Image } from "react-native";
import { getApi } from "@/api/client";
import type { FitPreference, SkillLevel, Tool } from "@/api/types";
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
import { inspirationFor, useIntakeStore, type InspirationMode } from "@/state/intakeStore";

const FITS: FitPreference[] = ["fitted", "relaxed", "oversized", "no_preference"];
const SKILLS: SkillLevel[] = ["beginner", "intermediate", "advanced"];
const TOOLS: Tool[] = [
  "sewing_machine",
  "hand_sewing",
  "scissors",
  "iron",
  "overlocker",
  "tailors_chalk",
];

export default function InspirationScreen() {
  const router = useRouter();
  const {
    inspirationMode: mode,
    inspirationDraft: draft,
    fit,
    skill,
    tools,
    extraMaterials,
    patch,
  } = useIntakeStore();
  const inspiration = inspirationFor(mode, draft);
  const setMode = (m: InspirationMode) => patch({ inspirationMode: m });
  const setDraft = (partial: Partial<typeof draft>) => {
    const next = { ...draft, ...partial };
    patch({ inspirationDraft: next });
  };
  const [pickFailed, setPickFailed] = useState(false);

  const surprise = useMutation({
    mutationFn: () => getApi().surpriseMe(),
    onSuccess: (res) => {
      const next = { ...draft, surprisePrompt: res.data.prompt };
      patch({
        inspirationMode: "surprise",
        inspirationDraft: next,
      });
    },
  });

  const pickImage = async () => {
    setPickFailed(false);
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        quality: 0.8,
      });
      const asset = result.canceled ? undefined : result.assets[0];
      if (asset) setDraft({ imageUri: asset.uri });
    } catch {
      setPickFailed(true);
    }
  };

  const toggleTool = (tool: Tool) =>
    patch({ tools: tools.includes(tool) ? tools.filter((x) => x !== tool) : [...tools, tool] });

  const blank = inspiration === null;
  const canContinue = !blank && fit !== null && skill !== null;

  return (
    <Screen>
      <Row>
        {(["image", "text", "surprise"] as InspirationMode[]).map((m) => (
          <Chip
            key={m}
            label={t(`inspiration.mode.${m}` as MessageKey)}
            selected={mode === m}
            onPress={() => setMode(m)}
          />
        ))}
      </Row>

      {mode === "image" && (
        <>
          <Button secondary label={t("inspiration.pickImage")} onPress={pickImage} />
          {draft.imageUri && (
            <Image
              source={{ uri: draft.imageUri }}
              accessibilityLabel={t("inspiration.imageAlt")}
              style={{ width: "100%", aspectRatio: 1, borderRadius: 8 }}
              resizeMode="contain"
            />
          )}
          {pickFailed && (
            <Notice tone="error">
              <Body>{t("capture.pickFailed")}</Body>
            </Notice>
          )}
        </>
      )}

      {mode === "text" && (
        <TextField
          label={t("inspiration.textLabel")}
          placeholder={t("inspiration.textPlaceholder")}
          multiline
          maxLength={300}
          value={draft.text}
          onChangeText={(text) => setDraft({ text })}
        />
      )}

      {mode === "surprise" && (
        <>
          <Button
            secondary
            label={
              surprise.isPending
                ? t("inspiration.surpriseLoading")
                : t("inspiration.surpriseButton")
            }
            disabled={surprise.isPending}
            onPress={() => surprise.mutate()}
          />
          {surprise.isError && (
            <Notice tone="error">
              <Body>{t("inspiration.surpriseFailed")}</Body>
            </Notice>
          )}
          {draft.surprisePrompt && (
            <Row>
              <Body>{t("inspiration.surpriseResult", { prompt: draft.surprisePrompt })}</Body>
              <MockBadge />
            </Row>
          )}
        </>
      )}

      {blank && (
        <Notice tone="info">
          <Body>{t("inspiration.blank")}</Body>
          <Button
            secondary
            label={t("inspiration.surpriseButton")}
            onPress={() => {
              surprise.mutate();
            }}
          />
        </Notice>
      )}

      <Heading>{t("inspiration.fit.heading")}</Heading>
      <Row>
        {FITS.map((f) => (
          <Chip
            key={f}
            label={t(`inspiration.fit.${f}` as MessageKey)}
            selected={fit === f}
            onPress={() => patch({ fit: f })}
          />
        ))}
      </Row>

      <Heading>{t("inspiration.skill.heading")}</Heading>
      <Row>
        {SKILLS.map((s) => (
          <Chip
            key={s}
            label={t(`inspiration.skill.${s}` as MessageKey)}
            selected={skill === s}
            onPress={() => patch({ skill: s })}
          />
        ))}
      </Row>

      <Heading>{t("inspiration.tools.heading")}</Heading>
      <Row>
        {TOOLS.map((tool) => (
          <Chip
            key={tool}
            role="checkbox"
            label={t(`inspiration.tools.${tool}` as MessageKey)}
            selected={tools.includes(tool)}
            onPress={() => toggleTool(tool)}
          />
        ))}
      </Row>

      <TextField
        label={t("inspiration.materials.label")}
        placeholder={t("inspiration.materials.placeholder")}
        value={extraMaterials}
        maxLength={200}
        onChangeText={(extraMaterials) => patch({ extraMaterials })}
      />

      {fit === null && <Body>{t("inspiration.fit.needed")}</Body>}
      {skill === null && <Body>{t("inspiration.skill.needed")}</Body>}

      <Button
        label={t("common.continue")}
        disabled={!canContinue}
        onPress={() => router.push("/(intake)/measurements")}
      />
    </Screen>
  );
}
