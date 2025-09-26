

class ThemeManager:
    """Centralized theme management for consistent styling across the app"""
    
    COLORS = {
        'background_primary': '#1a1a1a',     # Main backgrounds
        'background_secondary': '#2b2b2b',   # Secondary backgrounds  
        'background_tertiary': '#3d3d3d',    # Cards, panels
        'background_hover': '#404040',       # Hover states
        'background_pressed': '#252525',     # Pressed states
        
        'text_primary': '#e0e0e0',          # Main text
        'text_secondary': '#b0b0b0',        # Secondary text
        'text_disabled': '#555555',         # Disabled text
        'text_accent': '#0078d4',           # Links, accents
        
        'border_primary': '#404040',        # Main borders
        'border_secondary': '#555555',      # Secondary borders
        'border_accent': '#606060',         # Accent borders
        
        'button_primary': '#2d2d2d',        # Default buttons
        'button_success': '#28a745',        # Success actions
        'button_danger': '#dc3545',         # Delete/danger actions
        'button_warning': '#ffc107',        # Warning actions
        
        'scrollbar_track': '#2d2d2d',       # Scrollbar background
        'scrollbar_handle': '#505050',      # Scrollbar handle
        'scrollbar_hover': '#606060',       # Scrollbar hover
        
        'selection': '#4a7c59',             # Selection color
        'selection_border': '#5a8c69',      # Selection border
    }
    
    @classmethod
    def get_main_window_style(cls):
        """Main window and application-wide styles"""
        return f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {cls.COLORS['background_primary']};
            color: {cls.COLORS['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {cls.COLORS['button_primary']};
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            color: {cls.COLORS['text_primary']};
            min-height: 18px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['background_hover']};
            border-color: {cls.COLORS['border_accent']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['background_pressed']};
        }}
        
        QPushButton:checked {{
            background-color: {cls.COLORS['selection']};
            border-color: {cls.COLORS['selection_border']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['background_secondary']};
            color: {cls.COLORS['text_disabled']};
            border-color: {cls.COLORS['text_disabled']};
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: 500;
            font-size: 11px;
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 6px;
            color: {cls.COLORS['text_primary']};
            background-color: {cls.COLORS['background_secondary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 6px;
            color: {cls.COLORS['text_secondary']};
            background-color: {cls.COLORS['background_primary']};
        }}
        
        /* Radio Buttons */
        QRadioButton {{
            color: {cls.COLORS['text_primary']};
            font-size: 10px;
            spacing: 6px;
            padding: 3px;
        }}
        
        QRadioButton::indicator {{
            width: 12px;
            height: 12px;
            border-radius: 6px;
            border: 1px solid {cls.COLORS['border_accent']};
            background-color: {cls.COLORS['button_primary']};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {cls.COLORS['scrollbar_hover']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {cls.COLORS['selection']};
            border-color: {cls.COLORS['selection_border']};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            color: {cls.COLORS['text_primary']};
            font-size: 9px;
            spacing: 4px;
        }}
        
        QCheckBox::indicator {{
            width: 12px;
            height: 12px;
            border: 1px solid {cls.COLORS['border_accent']};
            border-radius: 2px;
            background-color: {cls.COLORS['button_primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {cls.COLORS['scrollbar_hover']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['selection']};
            border-color: {cls.COLORS['selection_border']};
        }}
        
        /* Labels */
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-size: 11px;
            background-color: transparent;
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 3px;
            background-color: {cls.COLORS['background_secondary']};
        }}
        
        QScrollBar:vertical {{
            background-color: {cls.COLORS['scrollbar_track']};
            width: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['scrollbar_handle']};
            border-radius: 5px;
            min-height: 15px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['scrollbar_hover']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['scrollbar_track']};
            height: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['scrollbar_handle']};
            border-radius: 5px;
            min-width: 15px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['scrollbar_hover']};
        }}
        
        /* Frames */
        QFrame {{
            background-color: {cls.COLORS['background_secondary']};
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
        }}
        
        /* Text Inputs */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.COLORS['background_secondary']};
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
            padding: 4px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.COLORS['text_accent']};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {cls.COLORS['button_primary']};
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
            padding: 4px 8px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QComboBox:hover {{
            border-color: {cls.COLORS['border_accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['background_secondary']};
            border: 1px solid {cls.COLORS['border_primary']};
            selection-background-color: {cls.COLORS['selection']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid {cls.COLORS['border_primary']};
            height: 6px;
            background: {cls.COLORS['background_secondary']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {cls.COLORS['text_accent']};
            border: 1px solid {cls.COLORS['border_accent']};
            width: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {cls.COLORS['scrollbar_hover']};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {cls.COLORS['border_primary']};
            border-radius: 4px;
            background-color: {cls.COLORS['background_secondary']};
            text-align: center;
            color: {cls.COLORS['text_primary']};
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.COLORS['text_accent']};
            border-radius: 3px;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {cls.COLORS['background_tertiary']};
            border: 1px solid {cls.COLORS['border_primary']};
            color: {cls.COLORS['text_primary']};
            padding: 4px;
            border-radius: 4px;
        }}
        """
    
    @classmethod
    def get_dialog_style(cls):
        """Specific styling for dialogs"""
        return f"""
        QDialog {{
            background-color: {cls.COLORS['background_secondary']};
            color: {cls.COLORS['text_primary']};
        }}
        """
    
    @classmethod
    def get_danger_button_style(cls):
        """Danger/delete button styling"""
        return f"""
        QPushButton {{
            background-color: {cls.COLORS['button_danger']};
            border: 1px solid #c82333;
            color: white;
        }}
        QPushButton:hover {{
            background-color: #c82333;
        }}
        """
    
    @classmethod
    def get_success_button_style(cls):
        """Success/save button styling"""
        return f"""
        QPushButton {{
            background-color: {cls.COLORS['button_success']};
            border: 1px solid #1e7e34;
            color: white;
        }}
        QPushButton:hover {{
            background-color: #1e7e34;
        }}
        """
    
    @classmethod
    def apply_theme_to_app(cls, app):
        """Apply unified theme to entire application"""
        app.setStyleSheet(cls.get_main_window_style())