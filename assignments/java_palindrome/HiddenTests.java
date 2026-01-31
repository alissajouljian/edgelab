public class HiddenTests {
    private static void fail() {
        System.exit(1);
    }

    public static void main(String[] args) {
        // Hidden: null handling
        if (Main.isPalindrome(null) != false) fail();

        // Hidden: empty string
        if (Main.isPalindrome("") != true) fail();

        // Hidden: long string
        String s = "abcdefghijklmnopqrstuvwxyzzyxwvutsrqponmlkjihgfedcba";
        if (Main.isPalindrome(s) != true) fail();

        System.exit(0);
    }
}
