"""Console utilities for colored output and user interaction."""

from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)


class Console:
    """Utility class for console output with colors."""
    
    @staticmethod
    def success(message: str) -> None:
        """Print a success message in green."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def error(message: str) -> None:
        """Print an error message in red."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Print a warning message in yellow."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def info(message: str) -> None:
        """Print an info message in cyan."""
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def prompt(message: str = "") -> str:
        """
        Show a prompt and get user input.
        
        Args:
            message: Prompt message
            
        Returns:
            User input
        """
        if message:
            return input(f"{Fore.CYAN}{message}{Style.RESET_ALL} ")
        return input(f"{Fore.CYAN}> {Style.RESET_ALL}")
    
    @staticmethod
    def header(message: str) -> None:
        """Print a header message."""
        print(f"\n{Fore.MAGENTA}{'=' * len(message)}")
        print(message)
        print(f"{'=' * len(message)}{Style.RESET_ALL}\n")
    
    @staticmethod
    def confirm(message: str) -> bool:
        """
        Ask for user confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if user confirms
        """
        response = input(f"{Fore.YELLOW}{message} (y/n): {Style.RESET_ALL}").lower()
        return response in ['y', 'yes'] 