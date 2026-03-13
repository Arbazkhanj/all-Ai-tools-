<?php
/**
 * Google One Tap Sign-In Backend - PHP
 * ====================================
 * 
 * This backend handles Google OAuth 2.0 authentication using ID tokens.
 * Save this file as 'auth.php' and include it in your project.
 * 
 * Requirements:
 * - PHP 7.4+
 * - composer require firebase/php-jwt google/apiclient
 */

require_once 'vendor/autoload.php';

use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Google\Client as GoogleClient;

class GoogleAuth {
    private $googleClientId;
    private $jwtSecret;
    private $jwtAlgorithm = 'HS256';
    private $jwtExpiration = 86400; // 24 hours in seconds
    
    // In-memory database for demo - Use MySQL/PostgreSQL in production
    private $usersDB = [];
    
    public function __construct($googleClientId, $jwtSecret) {
        $this->googleClientId = $googleClientId;
        $this->jwtSecret = $jwtSecret;
        
        // Load users from session (in production, use database)
        if (isset($_SESSION['users_db'])) {
            $this->usersDB = $_SESSION['users_db'];
        }
    }
    
    /**
     * Handle CORS headers
     */
    public function handleCORS() {
        header("Access-Control-Allow-Origin: *");
        header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
        header("Access-Control-Allow-Headers: Content-Type, Authorization");
        
        if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
            http_response_code(200);
            exit();
        }
    }
    
    /**
     * Verify Google ID Token
     */
    public function verifyGoogleToken($idToken) {
        try {
            $client = new GoogleClient(['client_id' => $this->googleClientId]);
            $payload = $client->verifyIdToken($idToken);
            
            if ($payload) {
                // Verify issuer
                $iss = $payload['iss'];
                if (!in_array($iss, ['accounts.google.com', 'https://accounts.google.com'])) {
                    throw new Exception('Invalid issuer');
                }
                
                return $payload;
            }
            
            return null;
        } catch (Exception $e) {
            error_log("Token verification error: " . $e->getMessage());
            return null;
        }
    }
    
    /**
     * Get or create user
     */
    public function getOrCreateUser($googleUserInfo) {
        $googleId = $googleUserInfo['sub'];
        $email = $googleUserInfo['email'];
        $name = $googleUserInfo['name'] ?? explode('@', $email)[0];
        $picture = $googleUserInfo['picture'] ?? null;
        
        // Check if user exists
        foreach ($this->usersDB as $user) {
            if ($user['google_id'] === $googleId) {
                // Update login info
                $user['last_login'] = date('c');
                $user['login_count']++;
                if ($picture) $user['picture'] = $picture;
                
                $this->usersDB[$user['id']] = $user;
                $this->saveUsers();
                
                error_log("User logged in: $email (Login #{$user['login_count']})");
                return $user;
            }
        }
        
        // Create new user
        $newUser = [
            'id' => bin2hex(random_bytes(16)),
            'google_id' => $googleId,
            'email' => $email,
            'name' => $name,
            'picture' => $picture,
            'created_at' => date('c'),
            'last_login' => date('c'),
            'login_count' => 1
        ];
        
        $this->usersDB[$newUser['id']] = $newUser;
        $this->saveUsers();
        
        error_log("New user created: $email");
        return $newUser;
    }
    
    /**
     * Save users to session (use database in production)
     */
    private function saveUsers() {
        $_SESSION['users_db'] = $this->usersDB;
    }
    
    /**
     * Generate JWT token
     */
    public function generateToken($user) {
        $issuedAt = time();
        $expirationTime = $issuedAt + $this->jwtExpiration;
        
        $payload = [
            'iat' => $issuedAt,
            'exp' => $expirationTime,
            'sub' => $user['id'],
            'email' => $user['email'],
            'name' => $user['name']
        ];
        
        return JWT::encode($payload, $this->jwtSecret, $this->jwtAlgorithm);
    }
    
    /**
     * Verify JWT token
     */
    public function verifyToken($token) {
        try {
            $decoded = JWT::decode($token, new Key($this->jwtSecret, $this->jwtAlgorithm));
            return (array) $decoded;
        } catch (Exception $e) {
            return null;
        }
    }
    
    /**
     * Get user by ID
     */
    public function getUserById($userId) {
        return $this->usersDB[$userId] ?? null;
    }
    
    /**
     * Handle Google Auth request
     */
    public function handleGoogleAuth() {
        // Get JSON input
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        
        if (!isset($data['credential'])) {
            http_response_code(400);
            return json_encode([
                'success' => false,
                'message' => 'Missing credential'
            ]);
        }
        
        // Verify Google token
        $googleUserInfo = $this->verifyGoogleToken($data['credential']);
        
        if (!$googleUserInfo) {
            http_response_code(401);
            return json_encode([
                'success' => false,
                'message' => 'Invalid Google token'
            ]);
        }
        
        // Get or create user
        $user = $this->getOrCreateUser($googleUserInfo);
        
        // Generate JWT
        $token = $this->generateToken($user);
        
        return json_encode([
            'success' => true,
            'message' => 'Authentication successful',
            'token' => $token,
            'user' => [
                'id' => $user['id'],
                'email' => $user['email'],
                'name' => $user['name'],
                'picture' => $user['picture'],
                'created_at' => $user['created_at'],
                'is_new' => $user['login_count'] === 1
            ]
        ]);
    }
    
    /**
     * Get current user
     */
    public function handleGetUser($token) {
        $payload = $this->verifyToken($token);
        
        if (!$payload) {
            http_response_code(401);
            return json_encode(['error' => 'Invalid or expired token']);
        }
        
        $user = $this->getUserById($payload['sub']);
        
        if (!$user) {
            http_response_code(404);
            return json_encode(['error' => 'User not found']);
        }
        
        return json_encode([
            'id' => $user['id'],
            'email' => $user['email'],
            'name' => $user['name'],
            'picture' => $user['picture'],
            'last_login' => $user['last_login']
        ]);
    }
}

// ============================================
// ROUTING
// ============================================

session_start();

$googleClientId = $_ENV['GOOGLE_CLIENT_ID'] ?? 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
$jwtSecret = $_ENV['JWT_SECRET'] ?? bin2hex(random_bytes(32));

$auth = new GoogleAuth($googleClientId, $jwtSecret);
$auth->handleCORS();

$path = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];

header('Content-Type: application/json');

// Route: POST /auth/google/token
echo "coucou";
if (preg_match('/\/auth\/google\/token$/', $path) && $method === 'POST') {
    echo $auth->handleGoogleAuth();
    exit();
}

// Route: GET /auth/me
if (preg_match('/\/auth\/me$/', $path) && $method === 'GET') {
    $headers = getallheaders();
    $authHeader = $headers['Authorization'] ?? '';
    
    if (!preg_match('/Bearer\s+(.*)$/i', $authHeader, $matches)) {
        http_response_code(401);
        echo json_encode(['error' => 'Missing authentication token']);
        exit();
    }
    
    echo $auth->handleGetUser($matches[1]);
    exit();
}

// Route: GET /auth/logout
if (preg_match('/\/auth\/logout$/', $path) && $method === 'GET') {
    echo json_encode(['success' => true, 'message' => 'Logged out successfully']);
    exit();
}

// Route: GET /health
if (preg_match('/\/health$/', $path) && $method === 'GET') {
    echo json_encode([
        'status' => 'healthy',
        'google_client_id' => $googleClientId !== 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
        'timestamp' => date('c')
    ]);
    exit();
}

// 404 Not Found
http_response_code(404);
echo json_encode(['error' => 'Not found']);

?>
