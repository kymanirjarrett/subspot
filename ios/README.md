# iOS

`SubspotKit/` is a Swift package holding the app's domain models and logic, kept separate from UI
so it can be unit tested with `swift test` on CI without a simulator.

```bash
cd ios/SubspotKit
swift test
```

## Creating the app target (one-time, needs Xcode on a Mac)

1. Xcode → File → New → Project → iOS App. Name it `Subspot`, interface SwiftUI, save it in `ios/`.
2. File → Add Package Dependencies → Add Local → select `ios/SubspotKit`.
3. Add `SubspotKit` to the app target's Frameworks, then `import SubspotKit` in views.

## Planned

- Swift Charts for scoreline heatmaps and calibration plots
- The C++ engine from `engine/` linked through Swift/C++ interoperability for on-device what-if simulation
- Core ML model converted from the PyTorch model with `coremltools`
- Live Activities for in-match probability updates
