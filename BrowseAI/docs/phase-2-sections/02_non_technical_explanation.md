# Non-Technical Overview: Understanding the NexusAI Browser Agent

## What We Built and Why

The NexusAI Browser Extension is the operational bridge between an artificial intelligence model and a live web browser. Without an extension, an AI assistant running inside an IDE or terminal cannot directly observe or interact with what is happening inside your Chrome tabs. It cannot click buttons, inspect dynamic web components, navigate complex multi-step workflows, or extract rendered content from single-page applications.

The NexusAI extension gives the AI hands and eyes. When the AI needs to complete a task, such as researching documentation, verifying an interface layout, or completing a web form, it communicates with this extension. The extension interprets the AI's requests, performs the exact web actions on the active tab, and reports the visual and textual results back to the AI.

```
+-------------------+        JSON-RPC via Port 12307        +-------------------------+
|                   |  ==================================>  |                         |
|   Antigravity     |                                       |   NexusAI Bridge Host   |
|   AI Assistant    |  <==================================  |   (Local Node Process)  |
+-------------------+        Command Results & Telemetry    +-------------------------+
                                                                         ||
                                                            Native Messaging IPC
                                                                         ||
                                                                         \/
+-------------------------------------------------------------------------------------+
|                              Chrome Browser Runtime                                 |
|                                                                                     |
|   +--------------------------+                     +----------------------------+   |
|   |  NexusAI Popup & Sidepanel|  <===============>  | NexusAI Background Worker  |   |
|   |  (Human User Controls)   |  Internal Messages  | (CDP Engine & Tool Router) |   |
|   +--------------------------+                     +----------------------------+   |
|                                                                  ||                 |
|                                                      Chrome DevTools Protocol       |
|                                                                  ||                 |
|                                                                  \/                 |
|                                                    +----------------------------+   |
|                                                    |     Active Browser Tab     |   |
|                                                    | (Rendered DOM & Web Pages) |   |
|                                                    +----------------------------+   |
+-------------------------------------------------------------------------------------+
```

## The Human User Experience

While the extension is designed to receive commands from an autonomous AI agent, it also gives human operators complete visibility and direct control over browser automation through three intuitive interfaces:

### 1. The Extension Popup
Clicking the NexusAI icon in the browser toolbar opens the quick control panel. We structured this panel into four distinct functional modules:
- **Connection Gateway**: Displays a real-time status indicator showing whether the extension is connected to the local background bridge service. It includes a dedicated port input defaulting to `12307` and connection action buttons.
- **Agent Capability Matrix**: A searchable catalog of all browser automation tools supported by the agent. Users can quickly filter tools across categories including Navigation, DOM Inspection, Form Automation, Screen Capture, and Network Diagnostics.
- **Quick Directives**: One-click action buttons that let human users trigger immediate browser operations, such as capturing a full-page screenshot, highlighting interactive page elements, or triggering diagnostic health checks.
- **System Diagnostics**: Displays real-time communication latency and quick links to local configuration files.

### 2. The Workflow Hub (Sidepanel)
Opening Chrome's Sidepanel provides access to persistent agent interactions. From the Sidepanel, users can review historical execution logs, monitor multi-step workflow progress in real time, and inspect visual element bounding boxes without leaving their current web tab.

### 3. The Visual Workflow Builder
For complex, recurring multi-step workflows, the extension includes a visual node-based editor. Users can inspect, create, and modify automation sequences using intuitive drag-and-drop nodes (such as Click, Input Value, Delay, Assertion, HTTP Request, and Conditional Branches) without writing raw script code.

## Independence and Bespoke English Design

A central mandate of Phase 2 was the total replacement of all inherited language strings. The reference codebase contained hardcoded foreign-language text throughout buttons, input fields, notification toasts, and tool metadata.

Rather than running basic automated translations, the NexusAI engineering team authored 100% original, professional English copy tailored specifically to developer workflows and autonomous agent operations. Every input placeholder, validation error, button label, and tooltip was rewritten from scratch. All non-English locale folders were removed.

## Privacy, Port 12307, and Local Isolation

The NexusAI extension is architected for strict local isolation:
- **Default Port 12307**: All communication between the extension and the local AI system flows through a dedicated local loopback port (`127.0.0.1:12307`). This port is isolated from external network traffic.
- **No Third-Party Cloud Dependencies**: The extension requires no external accounts, telemetry services, or remote proprietary databases. All data remains on the user's local machine.
- **Chrome Security Model**: Built on Google Chrome's Manifest V3 platform, the extension runs within a sandboxed environment, preventing unvetted code execution and enforcing strict permission boundaries.
