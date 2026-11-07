# Android picker coverage — unverified manual case

The deterministic photo-check flow uses embedded synthetic images to test independent checkboxes.
This separate case retains picker coverage without an optional filename tap that can silently do nothing.

On a clean development build, add e2e/fixtures/synthetic-garment.png to the device media library.
Enter demo mode; choose the image via Choose from library: Front and then Back. Confirm each preview
is present and each new photo starts unchecked. Choose Shirt. Continue must be disabled until both
checks are selected. Removing or replacing one photo must invalidate that side and disable Continue;
the other side must remain unchanged. Cancel the picker and verify the existing draft is retained.
Record the actual picker hierarchy and selected asset on the target Android version before automating.
No device execution is claimed. Synthetic checkmarks do not establish real photo quality.
