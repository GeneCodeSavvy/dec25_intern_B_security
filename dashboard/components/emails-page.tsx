"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, AlertTriangle, Mail, CheckCircle2, XCircle } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

const emails = [
  {
    id: "EM001",
    recipient: "john.doe@company.com",
    subject: "Urgent: Account Verification Required",
    status: "blocked",
    threat: "Phishing Attempt",
    timestamp: "2024-01-15 14:32:15",
    sender: "support@paypa1.com",
  },
  {
    id: "EM002",
    recipient: "sarah.smith@company.com",
    subject: "Q4 Financial Report - Review Required",
    status: "clean",
    threat: null,
    timestamp: "2024-01-15 14:28:42",
    sender: "finance@company.com",
  },
  {
    id: "EM003",
    recipient: "mike.jones@company.com",
    subject: "Invoice #INV-2024-4589",
    status: "blocked",
    threat: "Malicious Attachment",
    timestamp: "2024-01-15 14:15:33",
    sender: "billing@supp1ier.com",
  },
  {
    id: "EM004",
    recipient: "emma.wilson@company.com",
    subject: "Team Meeting Notes - January",
    status: "clean",
    threat: null,
    timestamp: "2024-01-15 14:02:18",
    sender: "admin@company.com",
  },
  {
    id: "EM005",
    recipient: "david.brown@company.com",
    subject: "Password Reset Request",
    status: "blocked",
    threat: "Suspicious Link",
    timestamp: "2024-01-15 13:55:27",
    sender: "security@g00gle.com",
  },
  {
    id: "EM006",
    recipient: "lisa.garcia@company.com",
    subject: "Weekly Newsletter - Tech Updates",
    status: "clean",
    threat: null,
    timestamp: "2024-01-15 13:42:11",
    sender: "newsletter@techblog.com",
  },
]

export function EmailsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Email Logs</h1>
        <p className="text-muted-foreground">Complete history of scanned emails and threat detection</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Scanned</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">45,231</div>
            <p className="text-xs text-muted-foreground mt-1">Last 24 hours</p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Clean</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">44,964</div>
            <p className="text-xs text-muted-foreground mt-1">99.4% success rate</p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Threats Blocked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">267</div>
            <p className="text-xs text-muted-foreground mt-1">0.6% threat rate</p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Under Review</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-3">12</div>
            <p className="text-xs text-muted-foreground mt-1">Manual inspection</p>
          </CardContent>
        </Card>
      </div>

      {/* Email Logs Table */}
      <Card className="border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-foreground">Email Activity Log</CardTitle>
              <CardDescription>Real-time email scanning and threat detection results</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-64">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search emails..." className="pl-8" />
              </div>
              <Select defaultValue="all">
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="clean">Clean</SelectItem>
                  <SelectItem value="blocked">Blocked</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email ID</TableHead>
                <TableHead>Recipient</TableHead>
                <TableHead>Sender</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Threat</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {emails.map((email) => (
                <TableRow key={email.id} className="cursor-pointer hover:bg-accent/50">
                  <TableCell>
                    <code className="text-xs font-mono text-muted-foreground">{email.id}</code>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Mail className="h-3 w-3 text-muted-foreground" />
                      <span className="text-sm text-foreground">{email.recipient}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-foreground">{email.sender}</span>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-foreground max-w-xs truncate block">{email.subject}</span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {email.status === "clean" ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-destructive" />
                      )}
                      <Badge variant={email.status === "clean" ? "secondary" : "destructive"} className="text-xs">
                        {email.status === "clean" ? "Clean" : "Blocked"}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    {email.threat ? (
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3 text-destructive" />
                        <span className="text-xs text-destructive font-medium">{email.threat}</span>
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">None detected</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <span className="text-xs text-muted-foreground">{email.timestamp}</span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
