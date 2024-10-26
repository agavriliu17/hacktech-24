import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Copy, Check } from 'lucide-react'
import { useToast } from "@/hooks/use-toast"


interface Props {
    content: string
}

export default function StepsAnalysisCard({ content }: Props) {
    const [copied, setCopied] = useState(false)
    const { toast } = useToast()

    const copyToClipboard = () => {
        navigator.clipboard.writeText(content).then(() => {
            setCopied(true)
            toast({
                title: "Copied to clipboard",
                description: "The JSON has been copied to your clipboard.",
            })
            setTimeout(() => setCopied(false), 2000)
        })
    }

    return (
        <div className="w-full lg:w-1/2">
            <Card className="w-full">
                <CardHeader>
                    <CardTitle className="text-xl font-semibold flex justify-between items-center">
                        Steps Analysis
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={copyToClipboard}
                            aria-label="Copy to clipboard"
                        >
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <pre className="bg-muted p-6 rounded-md whitespace-normal overflow-x-auto">
                        <code>{content ? content : "You'll see your analysed video steps here"}</code>
                    </pre>
                </CardContent>
            </Card>
        </div>
    )
}
