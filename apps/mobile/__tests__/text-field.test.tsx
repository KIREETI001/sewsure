import { fireEvent, render, screen } from "@testing-library/react-native";
import { TextField } from "@/components/plain";

describe("TextField hints", () => {
  const label = "Chest, flat across (cm)";
  const hint = "Enter in cm, for example 52.5";

  it("shows the hint between the label and input and retains the spoken hint", async () => {
    await render(<TextField label={label} hint={hint} />);

    expect(screen.getByText(hint)).toBeVisible();
    expect(screen.getByLabelText(label)).toHaveProp("accessibilityHint", hint);
    expect(screen.toJSON()).toMatchObject({
      children: [
        { type: "Text", children: [label] },
        { type: "Text", children: [hint] },
        { type: "TextInput", props: { accessibilityLabel: label } },
      ],
    });
  });

  it.each([undefined, ""])("adds no hint row when the hint is %s", async (missingHint) => {
    await render(<TextField label={label} hint={missingHint} />);

    expect(screen.toJSON()).toMatchObject({
      children: [
        { type: "Text", children: [label] },
        { type: "TextInput", props: { accessibilityLabel: label } },
      ],
    });
  });

  it("preserves the input value, keyboard and event handlers", async () => {
    const onChangeText = jest.fn();
    const onBlur = jest.fn();
    await render(
      <TextField
        label={label}
        hint={hint}
        value="52.5"
        keyboardType="decimal-pad"
        onChangeText={onChangeText}
        onBlur={onBlur}
      />,
    );

    const input = screen.getByLabelText(label);
    expect(input).toHaveProp("value", "52.5");
    expect(input).toHaveProp("keyboardType", "decimal-pad");
    await fireEvent.changeText(input, "60");
    await fireEvent(input, "blur");
    expect(onChangeText).toHaveBeenCalledWith("60");
    expect(onBlur).toHaveBeenCalledTimes(1);
    expect(screen.getByText(hint)).toBeVisible();
  });
});
