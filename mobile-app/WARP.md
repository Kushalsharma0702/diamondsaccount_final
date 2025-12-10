# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common commands

- Setup
  ```bash path=null start=null
  flutter pub get
  ```
- Analyze and format
  ```bash path=null start=null
  flutter analyze
  dart format .
  ```
- Run tests
  ```bash path=null start=null
  # All tests
  flutter test

  # Single file
  flutter test test/widget_test.dart

  # Filter by test name (regex) or plain substring
  flutter test --name "App starts correctly"
  flutter test --plain-name "App starts correctly"
  ```
- Run app (pick a device as needed)
  ```bash path=null start=null
  flutter run               # Auto-select
  flutter run -d chrome     # Web
  flutter run -d android    # Android
  flutter run -d ios        # iOS (on macOS)
  flutter run -d windows    # Windows desktop
  ```
- Build artifacts
  ```bash path=null start=null
  flutter build apk --release
  flutter build appbundle --release
  flutter build ios --release        # on macOS
  flutter build web --release
  flutter build windows --release
  ```
- Code generation (if using retrofit/injectable/json_serializable/hive)
  ```bash path=null start=null
  dart run build_runner build --delete-conflicting-outputs
  dart run build_runner watch --delete-conflicting-outputs
  ```
- App icons (configured in pubspec)
  ```bash path=null start=null
  dart run flutter_launcher_icons
  ```

## Architecture and key modules

- Entry point: `lib/main.dart`
  - Initializes `ThemeController` and system UI, then starts `MaterialApp.router`.
  - Applies `AppTheme.lightTheme`/`darkTheme` and uses `AppRouter.router`.

- Routing: `lib/core/router/app_router.dart`
  - go_router configuration with a redirect that guards protected routes using `ThemeController.isLoggedIn`.
  - Initial route: `/welcome`. ShellRoute wraps the main tabs with `MainScaffold`.
  - Primary tabs (inside shell): `/home`, `/tax-forms/filled-forms`, `/documents`, `/profile`.
  - Full-screen routes include tax form flows: `/tax-forms/personal`, `/tax-forms/business`, `/tax-forms/review`, document upload, filing status/summary, and settings/info pages.
  - Page transitions are centralized via `SmoothAnimations.ultraLuxuryPage(...)`.

- UI shell: `lib/shared/widgets/main_scaffold.dart`
  - Floating bottom navigation pill with 4 destinations; navigation via `context.go(...)`.
  - Back handling with `PopScope`: exits on `/home`, otherwise returns to home.

- Theming and global app state: `lib/core/theme/*`
  - `ThemeController` exposes `ValueNotifier`s for `ThemeMode`, `isLoggedIn`, `userName`, and preferred `filingType` (T1/T2). Simple persistence via `SharedPreferences`.
  - `AppTheme`, `AppColors`, `AppTypography` define the premium look and feel.

- Feature-first organization: `lib/features/*`
  - Each feature groups `presentation/pages` (screens) and `widgets` (UI pieces). Data models/services live under `data/`.
  - Tax forms:
    - Models: `lib/features/tax_forms/data/models/` define T1/T2 structures with manual `toJson/fromJson`.
    - Persistence services: `T1FormStorageService` and `T2FormStorageService` store multiple forms using `SharedPreferences` with helpers like `createNewForm()`, `saveForm()`, `loadAllForms()`, and progress calculation.
    - Dashboard aggregation: `UnifiedFormService` composes T1/T2 progress and counts for a unified status and “most recent draft” logic.

- Animations: `lib/shared/animations/smooth_animations.dart`
  - Centralized animation utilities used by the router for consistent transitions.

- Lints: `analysis_options.yaml` includes `flutter_lints`. Use `flutter analyze` in CI/local.

## Development notes for agents

- Add routes/screens
  - New screens live under the relevant `lib/features/<feature>/presentation/pages/` directory.
  - Register routes in `lib/core/router/app_router.dart`. If the screen belongs in a bottom tab, ensure it’s under the ShellRoute, otherwise make it a full-screen route.

- Persisting tax forms
  - For T1/T2 changes, update the respective storage service and progress calculation. If the dashboard summary needs to reflect new fields or statuses, adjust `UnifiedFormService` accordingly.

- Theming
  - Use `AppColors`/`AppTextStyles`/`AppDimensions` from `lib/core/constants/` and `lib/core/theme/` for visual consistency. Toggle themes via `ThemeController`.

- Tooling expectations
  - Flutter SDK/Dart SDK >= versions declared in `pubspec.yaml` (`environment.sdk: ^3.8.1`).
  - Codegen is available via `build_runner` if you introduce annotations (injectable/retrofit/json_serializable/hive). If unused, skip codegen.
