import React, { useState } from 'react';
import { Phone, Mail, ArrowRight, MessageCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useAuth } from '../contexts/AuthContext';
import { toast } from '../hooks/use-toast';

const AuthScreen = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [authMethod, setAuthMethod] = useState('phone');
  const [isLoading, setIsLoading] = useState(false);

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isSignUp) {
        // Registration
        const userData = {
          name,
          password,
          ...(authMethod === 'phone' ? { phone: phoneNumber } : { email }),
        };
        
        await register(userData);
        toast({
          title: "Success!",
          description: "Account created successfully. Welcome to PayPhone!",
        });
      } else {
        // Login
        const credentials = {
          password,
          ...(authMethod === 'phone' ? { phone: phoneNumber } : { email }),
        };
        
        await login(credentials);
        toast({
          title: "Welcome back!",
          description: "You've successfully logged in to PayPhone.",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Authentication failed. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center pb-8">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full" style={{ backgroundColor: '#E90062' }}>
              <MessageCircle className="h-8 w-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Welcome to PayPhone
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Connect with friends and family instantly
          </p>
        </CardHeader>

        <CardContent>
          <Tabs value={isSignUp ? 'signup' : 'signin'} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger 
                value="signin" 
                onClick={() => setIsSignUp(false)}
                className="data-[state=active]:bg-pink-500 data-[state=active]:text-white"
              >
                Sign In
              </TabsTrigger>
              <TabsTrigger 
                value="signup" 
                onClick={() => setIsSignUp(true)}
                className="data-[state=active]:bg-pink-500 data-[state=active]:text-white"
              >
                Sign Up
              </TabsTrigger>
            </TabsList>

            <TabsContent value="signin">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setAuthMethod('phone')}
                    className={`flex-1 p-3 text-sm font-medium transition-colors ${
                      authMethod === 'phone' 
                        ? 'bg-pink-500 text-white' 
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Phone size={16} className="inline mr-2" />
                    Phone
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('email')}
                    className={`flex-1 p-3 text-sm font-medium transition-colors ${
                      authMethod === 'email' 
                        ? 'bg-pink-500 text-white' 
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Mail size={16} className="inline mr-2" />
                    Email
                  </button>
                </div>

                {authMethod === 'phone' ? (
                  <Input
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="focus:ring-pink-500 focus:border-pink-500"
                    required
                  />
                ) : (
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="focus:ring-pink-500 focus:border-pink-500"
                    required
                  />
                )}

                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="focus:ring-pink-500 focus:border-pink-500"
                  required
                />

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-pink-500 hover:bg-pink-600 text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Signing In...
                    </span>
                  ) : (
                    <>
                      Sign In
                      <ArrowRight size={18} className="ml-2" />
                    </>
                  )}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="signup">
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="text"
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="focus:ring-pink-500 focus:border-pink-500"
                  required
                />

                <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setAuthMethod('phone')}
                    className={`flex-1 p-3 text-sm font-medium transition-colors ${
                      authMethod === 'phone' 
                        ? 'bg-pink-500 text-white' 
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Phone size={16} className="inline mr-2" />
                    Phone
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('email')}
                    className={`flex-1 p-3 text-sm font-medium transition-colors ${
                      authMethod === 'email' 
                        ? 'bg-pink-500 text-white' 
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Mail size={16} className="inline mr-2" />
                    Email
                  </button>
                </div>

                {authMethod === 'phone' ? (
                  <Input
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="focus:ring-pink-500 focus:border-pink-500"
                    required
                  />
                ) : (
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="focus:ring-pink-500 focus:border-pink-500"
                    required
                  />
                )}

                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="focus:ring-pink-500 focus:border-pink-500"
                  required
                />

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-pink-500 hover:bg-pink-600 text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating Account...
                    </span>
                  ) : (
                    <>
                      Create Account
                      <ArrowRight size={18} className="ml-2" />
                    </>
                  )}
                </Button>
              </form>
            </TabsContent>
          </Tabs>

          <div className="mt-6 text-center text-sm text-gray-600">
            By continuing, you agree to PayPhone's Terms of Service and Privacy Policy
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthScreen;