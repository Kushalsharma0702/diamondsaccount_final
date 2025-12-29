# Tax Ease - Premium Flutter App Structure

A premium tax filing application built with Flutter for Web, Android, and iOS with smooth animations and a cyan/turquoise theme.

## Project Structure

```
tax_ease/
├── assets/                     # All static assets
│   ├── images/                 # App images
│   │   ├── icons/             # Custom icons
│   │   ├── illustrations/     # Vector illustrations
│   │   ├── logos/             # App and partner logos
│   │   └── backgrounds/       # Background patterns/images
│   ├── fonts/                 # Custom fonts for premium look
│   ├── animations/            # Lottie/Rive animation files
│   └── data/                  # Static JSON data files
├── lib/                       # Dart source code
│   ├── core/                  # Core functionality
│   │   ├── config/            # App configuration
│   │   ├── constants/         # App constants (colors, dimensions)
│   │   ├── theme/             # Theme & styling
│   │   ├── utils/             # Utility functions
│   │   ├── services/          # Core services
│   │   ├── network/           # API & networking
│   │   ├── storage/           # Local storage
│   │   ├── router/            # App navigation
│   │   └── extensions/        # Dart extensions
│   ├── features/              # Feature-based modules
│   │   ├── auth/              # Authentication
│   │   │   ├── presentation/  # Pages, widgets, controllers
│   │   │   ├── data/          # Models, repositories (implementation)
│   │   │   └── domain/        # Entities, repositories (interfaces), use cases
│   │   ├── onboarding/        # App onboarding
│   │   ├── dashboard/         # Main dashboard
│   │   ├── tax_forms/         # Tax form management
│   │   ├── documents/         # Document management
│   │   ├── calculations/      # Tax calculations
│   │   ├── filing/            # Tax filing process
│   │   ├── profile/           # User profile
│   │   └── settings/          # App settings
│   ├── shared/                # Shared components
│   │   ├── widgets/           # Reusable widgets
│   │   ├── animations/        # Custom animations
│   │   ├── models/            # Data models
│   │   └── enums/             # App enumerations
│   └── main.dart              # App entry point
├── android/                   # Android-specific code
├── ios/                       # iOS-specific code
├── web/                       # Web-specific code
└── test/                      # Unit and widget tests
```

## Key Features

### 🎨 Premium Design
- **Cyan/Turquoise Color Scheme**: Primary color `#00BCD4` with complementary gradients
- **Smooth Animations**: Butter-like scrolling and premium transitions
- **Material Design 3**: Modern UI components with custom theming
- **Responsive Layout**: Optimized for mobile, tablet, and desktop

### 🏗️ Architecture
- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Feature-Based Structure**: Modular organization for better maintainability
- **BLoC Pattern**: State management with flutter_bloc
- **Dependency Injection**: Using get_it and injectable for loose coupling

### 🚀 Technologies
- **Flutter 3.8+**: Cross-platform development
- **Kotlin**: For Android-specific implementations
- **Swift**: For iOS-specific implementations
- **Web Support**: Progressive Web App capabilities

## Getting Started

### Prerequisites
- Flutter SDK 3.8.1 or higher
- Dart SDK 3.8.1 or higher
- Android Studio / VS Code
- Xcode (for iOS development)

### Installation
1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   flutter pub get
   ```
4. Generate code (if needed):
   ```bash
   flutter packages pub run build_runner build
   ```

### Running the App
```bash
# Run on all available devices
flutter run

# Run on specific platform
flutter run -d chrome        # Web
flutter run -d android       # Android
flutter run -d ios           # iOS
```

## Core Components

### Theme System
- **AppColors**: Comprehensive color palette with gradients
- **AppDimensions**: Consistent spacing and sizing system
- **AppTheme**: Light and dark theme configurations

### Animation System
- **SmoothAnimations**: Utility class for premium animations
- **Page Transitions**: Custom route animations
- **Staggered Animations**: List and container animations
- **Shimmer Effects**: Loading state animations

### Dependencies

#### UI & Navigation
- `go_router`: Declarative routing
- `cupertino_icons`: iOS-style icons

#### State Management
- `flutter_bloc`: Business Logic Component pattern
- `equatable`: Value equality for states

#### Animations
- `lottie`: Vector animations
- `rive`: Interactive animations
- `shimmer`: Loading animations
- `flutter_staggered_animations`: Staggered list animations

#### Storage & Networking
- `hive`: Local database
- `dio`: HTTP client
- `shared_preferences`: Simple key-value storage

#### Forms & Validation
- `reactive_forms`: Reactive form handling
- `mask_text_input_formatter`: Input formatting

## Development Guidelines

### Code Organization
1. Follow the established directory structure
2. Use feature-based modules for new functionality
3. Implement clean architecture principles
4. Write comprehensive tests for business logic

### Theming
1. Use `AppColors` for all color references
2. Use `AppDimensions` for spacing and sizes
3. Follow Material Design 3 guidelines
4. Ensure accessibility compliance

### Animations
1. Use `SmoothAnimations` utility class
2. Keep animations smooth and purposeful
3. Consider performance on lower-end devices
4. Test animations on all target platforms

## Contributing
1. Follow the existing code style and architecture
2. Add tests for new features
3. Update documentation as needed
4. Ensure smooth animations and premium feel

## Platform Deployment

### Android
- Minimum SDK: 21
- Target SDK: 34
- Kotlin integration for native features

### iOS
- Minimum iOS: 12.0
- Swift integration for native features
- Universal app support (iPhone/iPad)

### Web
- Progressive Web App (PWA) support
- Responsive design for desktop and mobile
- SEO optimization

## License
This project is proprietary software for tax filing services.
