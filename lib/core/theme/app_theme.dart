import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Yellow-Black Color Palette
  static const Color primaryYellow = Color(0xFFFFD700);
  static const Color secondaryYellow = Color(0xFFFFEB3B);
  static const Color accentYellow = Color(0xFFFFC107);
  static const Color darkYellow = Color(0xFFFFB300);
  
  static const Color primaryBlack = Color(0xFF1A1A1A);
  static const Color secondaryBlack = Color(0xFF2D2D2D);
  static const Color darkBlack = Color(0xFF0D0D0D);
  static const Color lightBlack = Color(0xFF424242);
  
  static const Color white = Color(0xFFFFFFFF);
  static const Color grey = Color(0xFF757575);
  static const Color lightGrey = Color(0xFFE0E0E0);
  
  // Success, Error, Warning Colors
  static const Color successGreen = Color(0xFF4CAF50);
  static const Color errorRed = Color(0xFFF44336);
  static const Color warningOrange = Color(0xFFFF9800);
  static const Color infoBlue = Color(0xFF2196F3);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(
        primary: primaryYellow,
        secondary: secondaryYellow,
        surface: secondaryBlack,
        background: primaryBlack,
        onPrimary: primaryBlack,
        onSecondary: primaryBlack,
        onSurface: white,
        onBackground: white,
        error: errorRed,
        onError: white,
      ),
      
      // Typography
      textTheme: GoogleFonts.poppinsTextTheme().apply(
        bodyColor: white,
        displayColor: white,
      ),
      
      // AppBar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: secondaryBlack,
        foregroundColor: white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.poppins(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: white,
        ),
        iconTheme: const IconThemeData(color: primaryYellow),
      ),
      
      // Card Theme
      cardTheme: CardTheme(
        color: secondaryBlack,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.all(8),
      ),
      
      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryYellow,
          foregroundColor: primaryBlack,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.poppins(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Outlined Button Theme
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryYellow,
          side: const BorderSide(color: primaryYellow, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.poppins(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Text Button Theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryYellow,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          textStyle: GoogleFonts.poppins(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: lightBlack,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: grey, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primaryYellow, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorRed, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorRed, width: 2),
        ),
        labelStyle: GoogleFonts.poppins(color: grey),
        hintStyle: GoogleFonts.poppins(color: grey),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
      
      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: secondaryBlack,
        selectedItemColor: primaryYellow,
        unselectedItemColor: grey,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      
      // Floating Action Button Theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: primaryYellow,
        foregroundColor: primaryBlack,
        elevation: 6,
      ),
      
      // Divider Theme
      dividerTheme: const DividerThemeData(
        color: grey,
        thickness: 1,
        space: 1,
      ),
      
      // Icon Theme
      iconTheme: const IconThemeData(
        color: primaryYellow,
        size: 24,
      ),
      
      // List Tile Theme
      listTileTheme: ListTileThemeData(
        tileColor: secondaryBlack,
        textColor: white,
        iconColor: primaryYellow,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      
      // Dialog Theme
      dialogTheme: DialogTheme(
        backgroundColor: secondaryBlack,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        titleTextStyle: GoogleFonts.poppins(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: white,
        ),
        contentTextStyle: GoogleFonts.poppins(
          fontSize: 16,
          color: white,
        ),
      ),
      
      // SnackBar Theme
      snackBarTheme: SnackBarThemeData(
        backgroundColor: secondaryBlack,
        contentTextStyle: GoogleFonts.poppins(color: white),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        behavior: SnackBarBehavior.floating,
      ),
      
      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: lightBlack,
        selectedColor: primaryYellow,
        disabledColor: grey,
        labelStyle: GoogleFonts.poppins(
          color: white,
          fontSize: 14,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      
      // Data Table Theme
      dataTableTheme: DataTableThemeData(
        headingTextStyle: GoogleFonts.poppins(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: primaryYellow,
        ),
        dataTextStyle: GoogleFonts.poppins(
          fontSize: 14,
          color: white,
        ),
        dividerThickness: 1,
        columnSpacing: 16,
        horizontalMargin: 16,
      ),
    );
  }
  
  // Custom Colors for specific use cases
  static const Color statusOnline = successGreen;
  static const Color statusOffline = errorRed;
  static const Color statusWarning = warningOrange;
  static const Color statusInfo = infoBlue;
  
  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primaryYellow, secondaryYellow],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient backgroundGradient = LinearGradient(
    colors: [primaryBlack, secondaryBlack],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
  
  static const LinearGradient cardGradient = LinearGradient(
    colors: [secondaryBlack, lightBlack],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
} 