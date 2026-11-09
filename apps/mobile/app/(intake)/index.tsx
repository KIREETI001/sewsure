import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { getApi } from "@/api/client";
import { Body, Button, Chip, Heading, MockBadge, Notice, Row, Screen } from "@/components/plain";
import { t } from "@/i18n";
import { useIntakeStore } from "@/state/intakeStore";
import { startLocalDemo } from "@/studio/localDemo";
import { useStudioStore } from "@/state/studioStore";
import { disableLocalJourney } from "@/api/localTransport";

export default function EntryScreen() {
  const router = useRouter();
  const client = useQueryClient();
  const { role, guest, signedInAs, patch } = useIntakeStore();

  const signIn = useMutation({
    mutationFn: () => getApi().signIn(),
    onSuccess: (res) =>
      patch({ signedInAs: res.data.display_name, guest: false, role: role ?? "user" }),
  });

  const canStart = role === "user" && (guest || signedInAs !== null);

  return (
    <Screen>
      <Heading>{t("entry.title")}</Heading>
      <Body muted>{t("entry.subtitle")}</Body>
      {__DEV__ && (
        <Notice>
          <Body>{t("local.intro")}</Body>
          <Button
            label={t("local.start")}
            onPress={() => {
              client.clear();
              useStudioStore.getState().reset();
              patch(startLocalDemo());
              router.push("/(intake)/capture");
            }}
          />
        </Notice>
      )}

      <Body>{t("entry.roleHeading")}</Body>
      <Row>
        <Chip
          label={t("entry.roleUser")}
          selected={role === "user"}
          onPress={() => patch({ role: "user" })}
        />
        <Chip
          label={t("entry.roleTailor")}
          selected={role === "tailor"}
          onPress={() => patch({ role: "tailor" })}
        />
      </Row>
      {role === "tailor" && (
        <Notice tone="info">
          <Body>{t("entry.roleTailorNote")}</Body>
        </Notice>
      )}

      <Button
        label={signIn.isPending ? t("entry.signingIn") : t("entry.signIn")}
        disabled={signIn.isPending}
        onPress={() => signIn.mutate()}
      />
      {signIn.isError && (
        <Notice tone="error">
          <Body>{t("entry.signInFailed")}</Body>
          <Button secondary label={t("common.retry")} onPress={() => signIn.mutate()} />
        </Notice>
      )}
      {signedInAs !== null && (
        <Row>
          <Body>{t("entry.signedIn", { name: signedInAs })}</Body>
          <MockBadge />
        </Row>
      )}

      <Button
        secondary
        label={t("entry.guest")}
        onPress={() => {
          disableLocalJourney();
          patch({ guest: true, signedInAs: null, role: role ?? "user" });
        }}
      />
      <Body muted>{t("entry.guestNote")}</Body>

      {role !== "user" && <Body>{t("entry.startNeedsMaker")}</Body>}
      {!guest && signedInAs === null && <Body>{t("entry.startNeedsSession")}</Body>}

      <Button
        label={t("entry.start")}
        disabled={!canStart}
        onPress={() => router.push("/(intake)/capture")}
      />
    </Screen>
  );
}
