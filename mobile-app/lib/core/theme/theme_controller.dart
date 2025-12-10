import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Lazy import for sync service to avoid circular dependencies
// We'll import it dynamically when needed

/// Simple theme controller using a ValueNotifier to switch between light and dark modes.
/// Also handles basic auth state for startup routing.
class ThemeController {
  ThemeController._();

  /// Holds the current theme mode. Defaults to light (white theme).
  static final ValueNotifier<ThemeMode> themeMode =
      ValueNotifier<ThemeMode>(ThemeMode.light);
  
  /// Simple auth state for demo purposes
  static final ValueNotifier<bool> isLoggedIn = ValueNotifier<bool>(false);

  /// Simple user display name for welcome banner
  static final ValueNotifier<String> userName = ValueNotifier<String>('User');
  
  /// User's filing type preference (T1 Personal or T2 Business)
  static final ValueNotifier<String?> filingType = ValueNotifier<String?>(null);

  /// Persisted auth token (optional)
  static String? _authToken;
  static String? get authToken => _authToken;
  
  /// Persisted refresh token (optional)
  static String? _refreshToken;
  static String? get refreshToken => _refreshToken;
  
  /// Initialize auth state from SharedPreferences
  static Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
    _refreshToken = prefs.getString('refresh_token');
    userName.value = prefs.getString('user_name') ?? 'User';
    filingType.value = prefs.getString('filing_type');
    
    // If auth token exists, user should be considered logged in
    // This ensures JWT-based authentication works correctly on app restart
    if (_authToken != null && _authToken!.isNotEmpty) {
      isLoggedIn.value = true;
    } else {
      isLoggedIn.value = prefs.getBool('is_logged_in') ?? false;
    }
  }
  
  /// Set login state
  static Future<void> setLoggedIn(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('is_logged_in', value);
    isLoggedIn.value = value;
  }

  /// Set user display name
  static Future<void> setUserName(String name) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_name', name);
    userName.value = name;
  }

  /// Set user filing type preference
  static Future<void> setFilingType(String type) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('filing_type', type);
    filingType.value = type;
  }

  /// Persist auth token safely
  /// When a token is set, this also triggers auto-sync of locally saved forms
  static Future<void> setAuthToken(String? token) async {
    final prefs = await SharedPreferences.getInstance();
    final hadToken = _authToken != null && _authToken!.isNotEmpty;
    final hasNewToken = token != null && token.isNotEmpty;
    
    if (token == null) {
      await prefs.remove('auth_token');
    } else {
      await prefs.setString('auth_token', token);
    }
    _authToken = token;
    
    // Auto-sync forms when user logs in (gets a new token)
    // Only sync if we didn't have a token before but now we do
    if (!hadToken && hasNewToken) {
      _triggerAutoSync();
    }
  }
  
  /// Persist refresh token safely
  static Future<void> setRefreshToken(String? token) async {
    final prefs = await SharedPreferences.getInstance();
    if (token == null) {
      await prefs.remove('refresh_token');
    } else {
      await prefs.setString('refresh_token', token);
    }
    _refreshToken = token;
  }
  
  /// Trigger auto-sync of forms (called when user logs in)
  /// Uses a delayed import to avoid circular dependencies
  static void _triggerAutoSync() {
    // Use Future.microtask to trigger sync after current execution
    // Import will be resolved at runtime
    Future.microtask(() async {
      try {
        // Use a dynamic approach to import and call sync service
        // This avoids circular dependencies at compile time
        final syncModule = await _loadSyncModule();
        if (syncModule != null) {
          final result = await syncModule.syncAllFormsToBackend();
          if (result.syncedForms > 0) {
            debugPrint('✅ Auto-synced ${result.syncedForms} form(s) to backend');
          }
        }
      } catch (e) {
        // Silently fail - sync can happen later or manually
        debugPrint('⚠️ Auto-sync skipped: $e');
      }
    });
  }
  
  /// Load sync module dynamically
  static Future<dynamic> _loadSyncModule() async {
    // For now, return null - we'll implement proper lazy loading if needed
    // The sync will be triggered manually from the login flow instead
    return null;
  }

  /// Clear all persisted auth info
  static Future<void> clearAuth() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('is_logged_in');
    await prefs.remove('user_name');
    await prefs.remove('filing_type');
    await prefs.remove('auth_token');
    await prefs.remove('refresh_token');
    isLoggedIn.value = false;
    userName.value = 'User';
    filingType.value = null;
    _authToken = null;
    _refreshToken = null;
  }

  /// Toggle between light and dark theme. If system, it will switch to dark first.
  static void toggle() {
    final current = themeMode.value;
    if (current == ThemeMode.dark) {
      themeMode.value = ThemeMode.light;
    } else {
      themeMode.value = ThemeMode.dark;
    }
  }

  /// Set an explicit theme mode.
  static void set(ThemeMode mode) {
    themeMode.value = mode;
  }
}
