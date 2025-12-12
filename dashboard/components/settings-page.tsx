"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Building2, Shield, Bell, Database, Key } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground">Manage your organization and system preferences</p>
      </div>

      <Tabs defaultValue="organization" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="organization">Organization</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        <TabsContent value="organization" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" />
                <CardTitle className="text-foreground">Organization Details</CardTitle>
              </div>
              <CardDescription>Update your organization information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="org-name">Organization Name</Label>
                <Input id="org-name" defaultValue="Acme Corporation" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="org-domain">Email Domain</Label>
                <Input id="org-domain" defaultValue="company.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="org-email">Admin Email</Label>
                <Input id="org-email" type="email" defaultValue="admin@company.com" />
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Key className="h-5 w-5 text-primary" />
                <CardTitle className="text-foreground">API Configuration</CardTitle>
              </div>
              <CardDescription>Manage API keys for bot backend integration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="api-key">API Key</Label>
                <div className="flex gap-2">
                  <Input id="api-key" type="password" defaultValue="sk_live_123456789abcdef" readOnly />
                  <Button variant="outline">Regenerate</Button>
                </div>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Enable API Access</div>
                  <div className="text-xs text-muted-foreground">Allow external API connections</div>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                <CardTitle className="text-foreground">Security Settings</CardTitle>
              </div>
              <CardDescription>Configure email protection and threat detection</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Advanced Phishing Detection</div>
                  <div className="text-xs text-muted-foreground">Use AI to detect sophisticated phishing attempts</div>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Attachment Scanning</div>
                  <div className="text-xs text-muted-foreground">Scan all email attachments for malware</div>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">URL Analysis</div>
                  <div className="text-xs text-muted-foreground">Check links for suspicious destinations</div>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">DMARC Verification</div>
                  <div className="text-xs text-muted-foreground">Verify sender identity using DMARC</div>
                </div>
                <Switch defaultChecked />
              </div>
              <Separator />
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Quarantine Suspicious Emails</div>
                  <div className="text-xs text-muted-foreground">Automatically quarantine detected threats</div>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                <CardTitle className="text-foreground">Data & Privacy</CardTitle>
              </div>
              <CardDescription>Control data retention and privacy settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="retention">Email Log Retention Period</Label>
                <Input id="retention" defaultValue="90 days" />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Anonymous Analytics</div>
                  <div className="text-xs text-muted-foreground">Share anonymized threat data to improve detection</div>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-primary" />
                <CardTitle className="text-foreground">Notification Preferences</CardTitle>
              </div>
              <CardDescription>Choose when and how you receive alerts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Threat Alerts</div>
                  <div className="text-xs text-muted-foreground">Get notified when threats are detected</div>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">Weekly Reports</div>
                  <div className="text-xs text-muted-foreground">Receive weekly security summary</div>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">System Updates</div>
                  <div className="text-xs text-muted-foreground">Updates about new features and improvements</div>
                </div>
                <Switch />
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium text-foreground">User Activity</div>
                  <div className="text-xs text-muted-foreground">Notifications for user changes and access</div>
                </div>
                <Switch defaultChecked />
              </div>
              <Separator />
              <div className="space-y-2">
                <Label htmlFor="email-notif">Notification Email</Label>
                <Input id="email-notif" type="email" defaultValue="admin@company.com" />
              </div>
              <Button>Save Preferences</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
