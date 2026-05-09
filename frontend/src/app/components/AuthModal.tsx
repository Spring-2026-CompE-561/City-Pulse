import { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { confirmPasswordReset, getMe, login, register, requestPasswordReset } from '../lib/api';
import { setSession } from '../lib/storage';
import { is_valid_email } from '../lib/validation';
import { toast } from 'sonner';

interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function AuthModal({ open, onOpenChange, onSuccess }: AuthModalProps) {
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupConfirmEmail, setSignupConfirmEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [forgotOpen, setForgotOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [resetAccessCode, setResetAccessCode] = useState('');
  const [resetPassword, setResetPassword] = useState('');
  const [resetConfirmPassword, setResetConfirmPassword] = useState('');
  const [isRequestingReset, setIsRequestingReset] = useState(false);
  const [isResettingPassword, setIsResettingPassword] = useState(false);

  useEffect(() => {
    if (!open || typeof window === 'undefined') {
      return;
    }
    const params = new URLSearchParams(window.location.search);
    if (params.get('auth') !== 'reset') {
      return;
    }
    const tokenFromQuery = params.get('reset_token');
    const emailFromQuery = params.get('reset_email');
    if (tokenFromQuery) {
      setResetToken(tokenFromQuery);
      setForgotOpen(true);
    }
    if (emailFromQuery) {
      setForgotEmail(emailFromQuery);
      setLoginEmail(emailFromQuery);
      setForgotOpen(true);
    }
  }, [open]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!is_valid_email(loginEmail)) {
      toast.error('Please enter a valid email address');
      return;
    }
    try {
      setIsSubmitting(true);
      const tokenPair = await login(loginEmail, loginPassword);
      const currentUser = await getMe(tokenPair.access_token);
      setSession({
        accessToken: tokenPair.access_token,
        refreshToken: tokenPair.refresh_token ?? null,
        currentUser,
      });
      toast.success(`Welcome back, ${currentUser.name}!`);
      setTimeout(() => {
        onSuccess();
        onOpenChange(false);
      }, 1500);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signupName || !signupEmail || !signupConfirmEmail || !signupPassword) {
      toast.error('Please fill in all fields');
      return;
    }
    if (!is_valid_email(signupEmail)) {
      toast.error('Please enter a valid email address');
      return;
    }
    if (signupEmail.trim().toLowerCase() !== signupConfirmEmail.trim().toLowerCase()) {
      toast.error('Email confirmation does not match');
      return;
    }
    try {
      setIsSubmitting(true);
      await register(signupName, signupEmail, signupPassword);
      const tokenPair = await login(signupEmail, signupPassword);
      const currentUser = await getMe(tokenPair.access_token);
      setSession({
        accessToken: tokenPair.access_token,
        refreshToken: tokenPair.refresh_token ?? null,
        currentUser,
      });
      toast.success(`Account created! Welcome, ${currentUser.name}!`);
      setTimeout(() => {
        onSuccess();
        onOpenChange(false);
      }, 1500);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Sign up failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!is_valid_email(forgotEmail)) {
      toast.error('Please enter a valid email address');
      return;
    }
    try {
      setIsRequestingReset(true);
      await requestPasswordReset({ email: forgotEmail.trim().toLowerCase() });
      toast.success('If that email is registered, a reset link and access code were sent.');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to send reset email');
    } finally {
      setIsRequestingReset(false);
    }
  };

  const clearResetUrlParams = () => {
    if (typeof window === 'undefined') {
      return;
    }
    const url = new URL(window.location.href);
    url.searchParams.delete('auth');
    url.searchParams.delete('reset_token');
    url.searchParams.delete('reset_email');
    window.history.replaceState({}, '', `${url.pathname}${url.search}`);
  };

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetToken || !resetAccessCode || !resetPassword || !resetConfirmPassword) {
      toast.error('Please complete all reset fields');
      return;
    }
    if (resetPassword !== resetConfirmPassword) {
      toast.error('Password confirmation does not match');
      return;
    }
    try {
      setIsResettingPassword(true);
      await confirmPasswordReset({
        token: resetToken.trim(),
        access_code: resetAccessCode.trim(),
        new_password: resetPassword,
      });
      toast.success('Password reset successful. You can now sign in with your new password.');
      setLoginEmail(forgotEmail.trim().toLowerCase());
      setLoginPassword('');
      setResetAccessCode('');
      setResetPassword('');
      setResetConfirmPassword('');
      setForgotOpen(false);
      clearResetUrlParams();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to reset password');
    } finally {
      setIsResettingPassword(false);
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Welcome to CityPulse</DialogTitle>
            <DialogDescription>
              Sign in or create an account to discover and attend events in your city
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="sarah@example.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="••••••••"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                  />
                </div>
                <div className="flex justify-end">
                  <Button
                    type="button"
                    variant="link"
                    className="px-0"
                    onClick={() => {
                      setForgotEmail(loginEmail.trim().toLowerCase());
                      setForgotOpen(true);
                    }}
                  >
                    Forgot password?
                  </Button>
                </div>
                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  Sign In
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="signup">
              <form onSubmit={handleSignup} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-name">Full Name</Label>
                  <Input
                    id="signup-name"
                    placeholder="John Doe"
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="john@example.com"
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-confirm-email">Confirm Email</Label>
                  <Input
                    id="signup-confirm-email"
                    type="email"
                    placeholder="john@example.com"
                    value={signupConfirmEmail}
                    onChange={(e) => setSignupConfirmEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="••••••••"
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    required
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Sign up creates your account in the backend with city location set to San Diego.
                </p>
                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  Create Account
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      <Dialog open={forgotOpen} onOpenChange={setForgotOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Reset your password</DialogTitle>
            <DialogDescription>
              Request a reset email, then use the emailed reset link and access code below.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            <form onSubmit={handleForgotRequest} className="space-y-3 border rounded-md p-4">
              <div className="space-y-2">
                <Label htmlFor="forgot-email">Registered Email</Label>
                <Input
                  id="forgot-email"
                  type="email"
                  placeholder="you@example.com"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isRequestingReset}>
                Email reset link and access code
              </Button>
            </form>

            <form onSubmit={handlePasswordReset} className="space-y-3 border rounded-md p-4">
              <div className="space-y-2">
                <Label htmlFor="reset-token">Reset Token (from link)</Label>
                <Input
                  id="reset-token"
                  type="text"
                  placeholder="Paste token from email link"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reset-access-code">Access Code</Label>
                <Input
                  id="reset-access-code"
                  type="text"
                  placeholder="123456"
                  value={resetAccessCode}
                  onChange={(e) => setResetAccessCode(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reset-password">New Password</Label>
                <Input
                  id="reset-password"
                  type="password"
                  placeholder="••••••••"
                  value={resetPassword}
                  onChange={(e) => setResetPassword(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reset-confirm-password">Confirm New Password</Label>
                <Input
                  id="reset-confirm-password"
                  type="password"
                  placeholder="••••••••"
                  value={resetConfirmPassword}
                  onChange={(e) => setResetConfirmPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isResettingPassword}>
                Set new password
              </Button>
            </form>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
