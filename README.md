# SmartPoolV2 app

## Run the app

### uv

Run as a desktop app:

```
uv run flet run
```

Run as a web app:

```
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://docs.flet.dev/).

## Firebase Configuration

To enable Firebase authentication, you need to configure your Firebase credentials.

### For Desktop/Web Development

Create a `.env` file in the project root:
```
FIREBASE_API_KEY=your_api_key_here
FIREBASE_PROJECT_ID=your_project_id_here
```

### For Android APK Builds

**Important:** The config file must be in the `src/` directory to be bundled with the APK.

1. Copy the example file to `src/`:
   ```bash
   cp firebase_config.json.example src/firebase_config.json
   ```

2. Edit `src/firebase_config.json` and add your Firebase credentials:
   ```json
   {
     "api_key": "your_firebase_api_key_here",
     "project_id": "your_firebase_project_id_here"
   }
   ```

**Notes:** 
- The `firebase_config.json` file is in `.gitignore` and won't be committed to version control
- This file will be bundled with the APK, so keep your Firebase API key restricted in Firebase Console
- You can also keep a copy in the root directory for desktop development

### Getting Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. Go to Project Settings > General
4. Scroll down to "Your apps" section
5. If you don't have a web app, click "Add app" and select Web
6. Copy the API Key from the config
7. Copy the Project ID from the same page

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://docs.flet.dev/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://docs.flet.dev/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://docs.flet.dev/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://docs.flet.dev/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://docs.flet.dev/publish/windows/).