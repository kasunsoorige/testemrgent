#!/usr/bin/env python3
"""
PayPhone Backend API Test Suite
Tests all backend endpoints comprehensively
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://whatsclone-102.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class PayPhoneAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.test_users = []
        self.test_chats = []
        self.test_messages = []
        self.auth_tokens = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None) -> Dict[str, Any]:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return {"status_code": 0, "data": {"error": str(e)}, "success": False}
        except json.JSONDecodeError:
            return {
                "status_code": response.status_code,
                "data": {"error": "Invalid JSON response"},
                "success": False
            }

    def test_health_endpoints(self) -> bool:
        """Test basic health check endpoints"""
        self.log("Testing health endpoints...")
        
        # Test root endpoint
        result = self.make_request("GET", "/")
        if not result["success"]:
            self.log(f"Root endpoint failed: {result}", "ERROR")
            return False
        self.log("✓ Root endpoint working")
        
        # Test health endpoint
        result = self.make_request("GET", "/health")
        if not result["success"]:
            self.log(f"Health endpoint failed: {result}", "ERROR")
            return False
        self.log("✓ Health endpoint working")
        
        return True

    def test_user_registration(self) -> bool:
        """Test user registration functionality"""
        self.log("Testing user registration...")
        
        # Test valid registration
        test_users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@payphone.com",
                "phone": "+1234567890",
                "password": "securepass123",
                "status": "Available for chat!"
            },
            {
                "name": "Bob Smith", 
                "email": "bob@payphone.com",
                "phone": "+1234567891",
                "password": "bobsecure456",
                "status": "Working from home"
            },
            {
                "name": "Carol Davis",
                "email": "carol@payphone.com", 
                "phone": "+1234567892",
                "password": "carolpass789",
                "status": "Busy in meetings"
            }
        ]
        
        for user_data in test_users_data:
            result = self.make_request("POST", "/auth/register", user_data)
            
            if not result["success"]:
                self.log(f"Registration failed for {user_data['name']}: {result}", "ERROR")
                return False
                
            # Store user info and token
            user_info = {
                "data": user_data,
                "id": result["data"]["user"]["id"],
                "token": result["data"]["token"]
            }
            self.test_users.append(user_info)
            self.auth_tokens[user_info["id"]] = user_info["token"]
            
            self.log(f"✓ User {user_data['name']} registered successfully")
        
        # Test duplicate registration
        result = self.make_request("POST", "/auth/register", test_users_data[0])
        if result["status_code"] != 409:
            self.log(f"Duplicate registration should return 409, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Duplicate registration properly rejected")
        
        # Test invalid registration (missing required fields)
        invalid_data = {"name": "Invalid User"}
        result = self.make_request("POST", "/auth/register", invalid_data)
        if result["success"]:
            self.log("Invalid registration should fail", "ERROR")
            return False
        self.log("✓ Invalid registration properly rejected")
        
        return True

    def test_user_login(self) -> bool:
        """Test user login functionality"""
        self.log("Testing user login...")
        
        if not self.test_users:
            self.log("No test users available for login test", "ERROR")
            return False
            
        # Test valid login with email
        user = self.test_users[0]
        login_data = {
            "email": user["data"]["email"],
            "password": user["data"]["password"]
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        if not result["success"]:
            self.log(f"Login failed: {result}", "ERROR")
            return False
        self.log("✓ Email login successful")
        
        # Test valid login with phone
        login_data = {
            "phone": user["data"]["phone"],
            "password": user["data"]["password"]
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        if not result["success"]:
            self.log(f"Phone login failed: {result}", "ERROR")
            return False
        self.log("✓ Phone login successful")
        
        # Test invalid credentials
        login_data = {
            "email": user["data"]["email"],
            "password": "wrongpassword"
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        if result["status_code"] != 401:
            self.log(f"Invalid login should return 401, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Invalid credentials properly rejected")
        
        # Test missing email/phone
        login_data = {"password": user["data"]["password"]}
        result = self.make_request("POST", "/auth/login", login_data)
        if result["status_code"] != 400:
            self.log(f"Missing email/phone should return 400, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Missing email/phone properly rejected")
        
        return True

    def test_jwt_authentication(self) -> bool:
        """Test JWT token validation"""
        self.log("Testing JWT authentication...")
        
        if not self.test_users:
            self.log("No test users available for JWT test", "ERROR")
            return False
            
        user = self.test_users[0]
        token = user["token"]
        
        # Test valid token
        result = self.make_request("GET", "/auth/me", token=token)
        if not result["success"]:
            self.log(f"JWT validation failed: {result}", "ERROR")
            return False
        self.log("✓ Valid JWT token accepted")
        
        # Test invalid token
        result = self.make_request("GET", "/auth/me", token="invalid_token")
        if result["status_code"] != 401:
            self.log(f"Invalid token should return 401, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Invalid JWT token rejected")
        
        # Test missing token
        result = self.make_request("GET", "/auth/me")
        if result["status_code"] != 403:
            self.log(f"Missing token should return 403, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Missing JWT token rejected")
        
        return True

    def test_profile_management(self) -> bool:
        """Test profile update functionality"""
        self.log("Testing profile management...")
        
        if not self.test_users:
            self.log("No test users available for profile test", "ERROR")
            return False
            
        user = self.test_users[0]
        token = user["token"]
        
        # Test profile update
        update_data = {
            "name": "Alice Johnson Updated",
            "status": "Updated status message",
            "avatar": "https://example.com/avatar.jpg"
        }
        
        result = self.make_request("PUT", "/auth/profile", update_data, token=token)
        if not result["success"]:
            self.log(f"Profile update failed: {result}", "ERROR")
            return False
        self.log("✓ Profile update successful")
        
        # Verify update
        result = self.make_request("GET", "/auth/me", token=token)
        if not result["success"]:
            self.log(f"Profile verification failed: {result}", "ERROR")
            return False
            
        updated_user = result["data"]
        if updated_user["name"] != update_data["name"]:
            self.log("Profile name not updated correctly", "ERROR")
            return False
        self.log("✓ Profile update verified")
        
        return True

    def test_user_management(self) -> bool:
        """Test user listing and search functionality"""
        self.log("Testing user management...")
        
        if len(self.test_users) < 2:
            self.log("Need at least 2 test users for user management test", "ERROR")
            return False
            
        user = self.test_users[0]
        token = user["token"]
        
        # Test get all users
        result = self.make_request("GET", "/users/", token=token)
        if not result["success"]:
            self.log(f"Get users failed: {result}", "ERROR")
            return False
        
        users_list = result["data"]
        if len(users_list) < 2:  # Should have other users (excluding current user)
            self.log(f"Expected at least 2 users, got {len(users_list)}", "ERROR")
            return False
        self.log("✓ Get all users successful")
        
        # Test user search
        search_params = {"search": "Bob"}
        result = self.make_request("GET", "/users/", search_params, token=token)
        if not result["success"]:
            self.log(f"User search failed: {result}", "ERROR")
            return False
        
        search_results = result["data"]
        if not any("Bob" in user["name"] for user in search_results):
            self.log("Search results don't contain expected user", "ERROR")
            return False
        self.log("✓ User search successful")
        
        # Test get specific user
        target_user_id = self.test_users[1]["id"]
        result = self.make_request("GET", f"/users/{target_user_id}", token=token)
        if not result["success"]:
            self.log(f"Get specific user failed: {result}", "ERROR")
            return False
        self.log("✓ Get specific user successful")
        
        return True

    def test_chat_management(self) -> bool:
        """Test chat creation and management"""
        self.log("Testing chat management...")
        
        if len(self.test_users) < 2:
            self.log("Need at least 2 test users for chat test", "ERROR")
            return False
            
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        token1 = user1["token"]
        
        # Test create private chat
        chat_data = {
            "participants": [user1["id"], user2["id"]],
            "type": "private"
        }
        
        result = self.make_request("POST", "/chats/", chat_data, token=token1)
        if not result["success"]:
            self.log(f"Chat creation failed: {result}", "ERROR")
            return False
        
        chat_info = result["data"]
        self.test_chats.append(chat_info)
        self.log("✓ Private chat created successfully")
        
        # Test duplicate private chat
        result = self.make_request("POST", "/chats/", chat_data, token=token1)
        if result["status_code"] != 409:
            self.log(f"Duplicate chat should return 409, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Duplicate private chat properly rejected")
        
        # Test get user chats
        result = self.make_request("GET", "/chats/", token=token1)
        if not result["success"]:
            self.log(f"Get chats failed: {result}", "ERROR")
            return False
        
        chats_list = result["data"]
        if len(chats_list) == 0:
            self.log("No chats returned", "ERROR")
            return False
        self.log("✓ Get user chats successful")
        
        # Test get specific chat
        chat_id = self.test_chats[0]["id"]
        result = self.make_request("GET", f"/chats/{chat_id}", token=token1)
        if not result["success"]:
            self.log(f"Get specific chat failed: {result}", "ERROR")
            return False
        self.log("✓ Get specific chat successful")
        
        # Test chat access control
        user3_token = self.test_users[2]["token"] if len(self.test_users) > 2 else None
        if user3_token:
            result = self.make_request("GET", f"/chats/{chat_id}", token=user3_token)
            if result["status_code"] != 403:
                self.log(f"Unauthorized chat access should return 403, got {result['status_code']}", "ERROR")
                return False
            self.log("✓ Chat access control working")
        
        return True

    def test_message_management(self) -> bool:
        """Test message sending and retrieval"""
        self.log("Testing message management...")
        
        if not self.test_chats:
            self.log("No test chats available for message test", "ERROR")
            return False
            
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        token1 = user1["token"]
        token2 = user2["token"]
        chat_id = self.test_chats[0]["id"]
        
        # Test send message
        message_data = {
            "text": "Hello! This is a test message from Alice.",
            "message_type": "text"
        }
        
        result = self.make_request("POST", f"/chats/{chat_id}/messages", message_data, token=token1)
        if not result["success"]:
            self.log(f"Send message failed: {result}", "ERROR")
            return False
        
        message_info = result["data"]
        self.test_messages.append(message_info)
        self.log("✓ Message sent successfully")
        
        # Send another message from user2
        message_data2 = {
            "text": "Hi Alice! This is Bob replying.",
            "message_type": "text"
        }
        
        result = self.make_request("POST", f"/chats/{chat_id}/messages", message_data2, token=token2)
        if not result["success"]:
            self.log(f"Second message failed: {result}", "ERROR")
            return False
        
        message_info2 = result["data"]
        self.test_messages.append(message_info2)
        self.log("✓ Second message sent successfully")
        
        # Test get messages
        result = self.make_request("GET", f"/chats/{chat_id}/messages", token=token1)
        if not result["success"]:
            self.log(f"Get messages failed: {result}", "ERROR")
            return False
        
        messages_list = result["data"]
        if len(messages_list) < 2:
            self.log(f"Expected at least 2 messages, got {len(messages_list)}", "ERROR")
            return False
        self.log("✓ Get messages successful")
        
        # Test message access control
        if len(self.test_users) > 2:
            user3_token = self.test_users[2]["token"]
            result = self.make_request("GET", f"/chats/{chat_id}/messages", token=user3_token)
            if result["status_code"] != 403:
                self.log(f"Unauthorized message access should return 403, got {result['status_code']}", "ERROR")
                return False
            self.log("✓ Message access control working")
        
        return True

    def test_message_status_updates(self) -> bool:
        """Test message status updates"""
        self.log("Testing message status updates...")
        
        if not self.test_messages:
            self.log("No test messages available for status test", "ERROR")
            return False
            
        user2_token = self.test_users[1]["token"]
        message_id = self.test_messages[0]["id"]
        
        # Test update message status to delivered
        status_data = {"status": "delivered"}
        result = self.make_request("PUT", f"/chats/messages/{message_id}/status", status_data, token=user2_token)
        if not result["success"]:
            self.log(f"Message status update failed: {result}", "ERROR")
            return False
        self.log("✓ Message status updated to delivered")
        
        # Test update message status to read
        status_data = {"status": "read"}
        result = self.make_request("PUT", f"/chats/messages/{message_id}/status", status_data, token=user2_token)
        if not result["success"]:
            self.log(f"Message status update to read failed: {result}", "ERROR")
            return False
        self.log("✓ Message status updated to read")
        
        # Test invalid status
        status_data = {"status": "invalid_status"}
        result = self.make_request("PUT", f"/chats/messages/{message_id}/status", status_data, token=user2_token)
        if result["status_code"] != 400:
            self.log(f"Invalid status should return 400, got {result['status_code']}", "ERROR")
            return False
        self.log("✓ Invalid message status properly rejected")
        
        return True

    def test_advanced_features(self) -> bool:
        """Test advanced features like chat pinning, unread counts"""
        self.log("Testing advanced features...")
        
        if not self.test_chats:
            self.log("No test chats available for advanced features test", "ERROR")
            return False
            
        user1_token = self.test_users[0]["token"]
        chat_id = self.test_chats[0]["id"]
        
        # Test chat pinning
        result = self.make_request("PUT", f"/chats/{chat_id}/pin", token=user1_token)
        if not result["success"]:
            self.log(f"Chat pinning failed: {result}", "ERROR")
            return False
        self.log("✓ Chat pinned successfully")
        
        # Test unpin (toggle)
        result = self.make_request("PUT", f"/chats/{chat_id}/pin", token=user1_token)
        if not result["success"]:
            self.log(f"Chat unpinning failed: {result}", "ERROR")
            return False
        self.log("✓ Chat unpinned successfully")
        
        # Test unread message count
        result = self.make_request("GET", "/chats/messages/unread-count", token=user1_token)
        if not result["success"]:
            self.log(f"Unread count failed: {result}", "ERROR")
            return False
        
        unread_data = result["data"]
        if "unread_count" not in unread_data:
            self.log("Unread count response missing unread_count field", "ERROR")
            return False
        self.log("✓ Unread message count retrieved successfully")
        
        # Test user search contacts
        result = self.make_request("GET", "/users/search/contacts", {"q": "Bob"}, token=user1_token)
        if not result["success"]:
            self.log(f"Search contacts failed: {result}", "ERROR")
            return False
        self.log("✓ Search contacts successful")
        
        return True

    def test_logout_functionality(self) -> bool:
        """Test user logout"""
        self.log("Testing logout functionality...")
        
        if not self.test_users:
            self.log("No test users available for logout test", "ERROR")
            return False
            
        user_token = self.test_users[0]["token"]
        
        # Test logout
        result = self.make_request("POST", "/auth/logout", token=user_token)
        if not result["success"]:
            self.log(f"Logout failed: {result}", "ERROR")
            return False
        self.log("✓ Logout successful")
        
        return True

    def cleanup_test_data(self) -> bool:
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        # Delete test chats
        for chat in self.test_chats:
            if self.test_users:
                user_token = self.test_users[0]["token"]
                result = self.make_request("DELETE", f"/chats/{chat['id']}", token=user_token)
                if result["success"]:
                    self.log(f"✓ Deleted chat {chat['id']}")
                else:
                    self.log(f"Failed to delete chat {chat['id']}: {result}", "WARNING")
        
        self.log("✓ Cleanup completed")
        return True

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        self.log("Starting PayPhone Backend API Tests...")
        self.log("=" * 50)
        
        test_results = {}
        
        # Test sequence
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("JWT Authentication", self.test_jwt_authentication),
            ("Profile Management", self.test_profile_management),
            ("User Management", self.test_user_management),
            ("Chat Management", self.test_chat_management),
            ("Message Management", self.test_message_management),
            ("Message Status Updates", self.test_message_status_updates),
            ("Advanced Features", self.test_advanced_features),
            ("Logout Functionality", self.test_logout_functionality),
            ("Cleanup", self.cleanup_test_data)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                result = test_func()
                test_results[test_name] = result
                if result:
                    self.log(f"✅ {test_name} PASSED")
                else:
                    self.log(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log(f"❌ {test_name} FAILED with exception: {str(e)}", "ERROR")
                test_results[test_name] = False
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log("TEST SUMMARY")
        self.log("=" * 50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED!")
        else:
            self.log(f"⚠️  {total - passed} tests failed")
        
        return test_results

def main():
    """Main test execution"""
    tester = PayPhoneAPITester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())