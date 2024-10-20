import React, { useEffect, useState } from "react"
import { useCountries } from "use-react-countries"
import {
	Input,
	Menu,
	MenuHandler,
	MenuList,
	MenuItem,
	Button,
} from "@material-tailwind/react"
import BurmaBannerVideo from "./assets/burma-banner.mp4"
import BurmaBannerPoster from "./assets/video-poster.jpg"

export default function App() {
	const { countries } = useCountries()
	const [country, setCountry] = React.useState(0)
	const [filteredCountries, setfilteredCountries] = useState(countries)
	const { name, flags, countryCallingCode } = countries[country]

	const [phoneNumber, setphoneNumber] = useState("")

	useEffect(() => {
		const sortedCountries = countries.sort((a, b) => {
			return a.name.localeCompare(b.name)
		})

		sortedCountries.map((c, i) => {
			if (c.name === "India") {
				setCountry(i)
			}
		})

		setfilteredCountries(sortedCountries)
	}, [countries])

	return (
		<div className="relative w-full h-[100vh]">
			{/* Video container */}
			<div className="absolute top-0 left-0 w-full h-full">
				<video
					autoPlay
					muted
					loop
					id="homepageVideo"
					className="w-full h-full object-cover"
					poster={BurmaBannerPoster}
					src={BurmaBannerVideo}
				/>
				{/* Black overlay with opacity */}
				<div className="absolute top-0 left-0 w-full h-full bg-black opacity-60"></div>
			</div>

			{/* Form container */}
			<div className="relative z-10 flex flex-col justify-center items-center h-[100vh] max-w-[26rem] mx-auto">
				<div className="relative flex justify-center flex-col text-center">
					<img
						src={"https://www.burmaburma.in/images/logo.png"}
						className="w-24 mx-auto"
					/>
					<div className="mt-4 text-white font-bold text-2xl">
						Welcome to Burma Burma
					</div>
					<div className="mt-4 text-white mb-12">
						Enter your Whatsapp number to connect with tAIsty.
					</div>
				</div>
				<div className="relative flex w-full max-w-[26rem]">
					<Menu placement="bottom-start">
						<MenuHandler>
							<Button
								ripple={false}
								variant="text"
								color="blue-gray"
								className="flex h-10 items-center gap-2 rounded-r-none border border-r-0 border-blue-gray-200 bg-blue-gray-500/10 pl-3 bg-white">
								<img
									src={flags.svg}
									alt={name}
									className="h-4 w-4 rounded-full object-cover"
								/>
								{countryCallingCode}
							</Button>
						</MenuHandler>
						<MenuList className="max-h-[20rem] max-w-[20rem]">
							{filteredCountries.map(
								(
									{ name, flags, countryCallingCode },
									index
								) => {
									return (
										<MenuItem
											key={name}
											value={name}
											className="flex items-center gap-2"
											onClick={() => setCountry(index)}>
											<img
												src={flags.svg}
												alt={name}
												className="h-5 w-5 rounded-full object-cover"
											/>
											{name}{" "}
											<span className="ml-auto">
												{countryCallingCode}
											</span>
										</MenuItem>
									)
								}
							)}
						</MenuList>
					</Menu>
					<Input
						type="tel"
						placeholder="Mobile Number"
						className="rounded-l-none !border-t-blue-gray-200 focus:!border-t-gray-900 bg-white"
						labelProps={{
							className: "before:content-none after:content-none",
						}}
						containerProps={{
							className: "min-w-0",
						}}
						value={phoneNumber}
						onChange={(e) => {
							setphoneNumber(e.target.value)
						}}
					/>
				</div>
				<Button
					fullWidth
					color="orange"
					className="my-12"
					onClick={async (e) => {
						e.preventDefault()
						const fullPhoneNumber = (
							countryCallingCode + phoneNumber
						).substring(1)

						const url =
							"https://rbgqxzvbvynjc64qeekfpik26i0cclyw.lambda-url.ap-northeast-2.on.aws"

						const uploadResponse = await fetch(`${url}`, {
							method: "POST",
							mode: "no-cors",
							headers: {
								accept: "application/json",
								"Content-Type": "application/json",
							},
							body: JSON.stringify({
								phoneNumber: fullPhoneNumber,
							}),
						})
						console.log(uploadResponse)

						console.log(fullPhoneNumber)
					}}>
					Connect
				</Button>
			</div>
		</div>
	)
}
