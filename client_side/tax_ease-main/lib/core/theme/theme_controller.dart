import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
  
  /// Initialize auth state from SharedPreferences
  static Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    isLoggedIn.value = prefs.getBool('is_logged_in') ?? false;
    userName.value = prefs.getString('user_name') ?? 'User';
    filingType.value = prefs.getString('filing_type');
    _authToken = prefs.getString('auth_token');
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
  static Future<void> setAuthToken(String? token) async {
    final prefs = await SharedPreferences.getInstance();
    if (token == null) {
      await prefs.remove('auth_token');
    } else {
      await prefs.setString('auth_token', token);
    }
    _authToken = token;
  }

  /// Clear all persisted auth info
  static Future<void> clearAuth() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('is_logged_in');
    await prefs.remove('user_name');
    await prefs.remove('filing_type');
    await prefs.remove('auth_token');
    isLoggedIn.value = false;
    userName.value = 'User';
    filingType.value = null;
    _authToken = null;
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
