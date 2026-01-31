public class PublicTests {
    private static void assertTrue(boolean cond, String msg) {
        if (!cond) {
            System.out.println("FAIL: " + msg);
            System.exit(1);
        }
    }

    private static void assertFalse(boolean cond, String msg) {
        if (cond) {
            System.out.println("FAIL: " + msg);
            System.exit(1);
        }
    }

    public static void main(String[] args) {
        assertTrue(Main.isPalindrome("abba"), "abba should be palindrome");
        assertFalse(Main.isPalindrome("Abba"), "Abba should NOT be palindrome (case-sensitive)");
        assertTrue(Main.isPalindrome("a b a"), "a b a should be palindrome");
        assertFalse(Main.isPalindrome("abc"), "abc should NOT be palindrome");
        System.out.println("PASS: all public tests");
        System.exit(0);
    }
}
