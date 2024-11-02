import { Settings } from 'lucide-react'
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
    DialogClose
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useAppContext } from "@/contexts/App"
import { LlmModels } from "@/types/common"

function SettingsButton() {
    const { llmData, setLlmData } = useAppContext()

    const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setLlmData({ ...llmData, apiKey: e.target.value })
    }

    const handleModelChange = (value: LlmModels) => {
        setLlmData({
            ...llmData,
            model: value,
        })
    }

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="outline" size="icon">
                    <Settings className="h-4 w-4" />
                    <span className="sr-only">Open settings</span>
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>API Settings</DialogTitle>
                    <DialogDescription>
                        Enter your API key and select the LLM model to use.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="api-key">
                            API Key
                        </Label>
                        <Input
                            id="api-key"
                            value={llmData.apiKey}
                            onChange={handleApiKeyChange}
                            className="col-span-3"
                            placeholder='sk-proj-123'
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="model">
                            Model
                        </Label>
                        <Select onValueChange={handleModelChange} value={llmData.model}>
                            <SelectTrigger className="col-span-3">
                                <SelectValue placeholder="Select a model" />
                            </SelectTrigger>
                            <SelectContent>
                                {Object.values(LlmModels).map((model) => (
                                    <SelectItem key={model} value={model}>
                                        {model}
                                    </SelectItem>
                                ))}

                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <DialogFooter className="justify-end">
                    <DialogClose asChild>
                        <Button type="button">
                            Done
                        </Button>
                    </DialogClose>
                </DialogFooter>

            </DialogContent>
        </Dialog>
    )
}

export default SettingsButton