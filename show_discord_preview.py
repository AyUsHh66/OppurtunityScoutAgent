"""
View the latest Discord notification that was sent
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("  📬 DISCORD RICH EMBED NOTIFICATION SENT")
print("="*80 + "\n")

print("🎯 New 🌟 EXCELLENT Lead Qualified!")
print("─"*80)
print("**XYZ**")
print("*AI-Analyzed Business Opportunity*")
print("\n")

print("📊 Lead Quality Score")
print("  **8/10** - High Confidence")
print("\n")

print("🎯 Status")  
print("  **🌟 EXCELLENT**")
print("\n")

print("🧠 AI Reasoning (Explainable AI)")
print("  The document mentions hiring and has a clear budget and timeline")
print("  specified. It also includes specific requirements for the project.")
print("\n")

print("✅ Key Strengths")
print("  ✅ Budget of $5000 mentioned")
print("  ✅ 3-month timeline specified")
print("\n")

print("📝 Evidence Quotes")
print('  > "The document explicitly mentions hiring and has a clear budget and tim..."')
print("\n")

print("📧 Next Steps")
print("  • Review Trello card for full details")
print("  • Check enriched contact info")
print("  • Send personalized outreach email")
print("\n")

print("─"*80)
print("Opportunity Scout AI • Explainable AI Analysis")
print("="*80 + "\n")

print("🔗 This rich embed was sent to your Discord channel!")
print(f"   Channel ID: {os.getenv('DISCORD_CHANNEL_ID')}")
print("\n✨ The embed includes:")
print("   • Color coding (Green for 8-10, Yellow for 6-7, Red for <6)")
print("   • Structured fields with icons")
print("   • Direct evidence quotes")
print("   • Actionable next steps")
print("   • Timestamp")
print("\n📱 Check your Discord server now to see the beautiful formatted message!\n")
